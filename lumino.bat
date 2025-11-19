@echo off
:: ==========================================
:: LAUNCHER LUMINO ASSISTANT
:: ==========================================

:: Perintah ini akan membuka Windows Terminal (wt)
:: -p "Lumino"                     : Menggunakan profile khusus yang tadi dibuat
:: -d "D:\_PROJEK_PRIBADI\AIAgent" : Memaksa terminal start di folder project (PENTING)
:: cmd /k "python main.py"         : Menjalankan script python dan menjaga jendela tetap terbuka

start "D:\_PROJEK_PRIBADI\AIAgent" cmd /k "python main.py"

exit