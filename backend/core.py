import time
import sys
import os
import gc
from llama_cpp import Llama

# --- IMPORT KONFIGURASI BARU ---
from backend import config
from backend.config import ModelConfig

# --- PEREDAM SUARA ---
class SuppressFactory:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._devnull = open(os.devnull, 'w', encoding='utf-8')
        sys.stdout = self._devnull
        sys.stderr = self._devnull
        try:
            self._orig_fd1 = os.dup(1)
            self._orig_fd2 = os.dup(2)
            os.dup2(self._devnull.fileno(), 1)
            os.dup2(self._devnull.fileno(), 2)
        except:
            self._orig_fd1 = None
            self._orig_fd2 = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._orig_fd1 is not None:
            os.dup2(self._orig_fd1, 1)
            os.close(self._orig_fd1)
        if self._orig_fd2 is not None:
            os.dup2(self._orig_fd2, 2)
            os.close(self._orig_fd2)
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._devnull.close()

class AIEngine:
    def __init__(self):
        self.model = None
        self.active_config = None
        self.history = [] # Context Memory
        
        # Auto-load first available model by default
        available_models = config.get_available_models()
        if available_models:
            self.switch_model(available_models[0])
        else:
            print("Error: No models found.")

    def switch_model(self, model_filename):
        """
        Switch the active model to the specified filename.
        Returns True if successful, False otherwise.
        """
        try:
            self.active_config = ModelConfig(model_filename)
            self.load_model()
            self.history = [] # Reset history on model switch
            return True
        except Exception as e:
            print(f"Error switching model: {e}")
            return False

    def load_model(self):
        # CLEANUP MEMORY
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            time.sleep(1)

        try:
            with SuppressFactory():
                self.model = Llama(**self.active_config.init_params)
        except Exception as e:
            print(f"Error loading model: {e}")
            return 

    def generate_response(self, user_input, stream=False):
        if not self.model: return "Error: Neural Core not active."

        # 1. Update History
        current_message = {"role": "user", "content": user_input}
        
        # 2. Prepare Messages for Chat Completion
        messages = list(self.history) # Copy existing history
        messages.append(current_message)
        self.history.append(current_message)

        # 3. Generate using create_chat_completion (High-level API)
        try:
            # Filter out parameters not supported by create_chat_completion (like 'echo')
            gen_params = self.active_config.gen_params.copy()
            if "echo" in gen_params:
                del gen_params["echo"]

            # Calculate Prompt Tokens (Estimate)
            prompt_tokens = 0
            try:
                for msg in messages:
                    if isinstance(msg['content'], str):
                        prompt_tokens += len(self.model.tokenize(msg['content'].encode('utf-8')))
            except:
                pass

            output = self.model.create_chat_completion(
                messages=messages,
                stream=stream,
                **gen_params
            )
            
            if stream:
                # Generator wrapper to capture full response for history
                full_response = ""
                completion_tokens = 0
                
                for chunk in output:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        text_chunk = delta['content']
                        full_response += text_chunk
                        completion_tokens += 1 # Rough count of chunks/tokens
                        yield {"type": "content", "data": text_chunk}
                
                # Append assistant response to history after streaming is done
                self.history.append({"role": "assistant", "content": full_response})
                
                # Yield Usage Stats
                # Recalculate exact output tokens
                try:
                    completion_tokens = len(self.model.tokenize(full_response.encode('utf-8')))
                except:
                    pass
                    
                yield {
                    "type": "usage", 
                    "data": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                }
                
            else:
                text_response = output['choices'][0]['message']['content']
                self.history.append({"role": "assistant", "content": text_response})
                
                # Calculate tokens
                completion_tokens = 0
                try:
                    completion_tokens = len(self.model.tokenize(text_response.encode('utf-8')))
                except:
                    pass
                    
                return {
                    "content": text_response,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                }

        except Exception as e:
            error_msg = f"Runtime Logic Error: {str(e)}"
            if stream:
                yield {"type": "content", "data": error_msg}
            else:
                return {"content": error_msg}

engine = AIEngine()