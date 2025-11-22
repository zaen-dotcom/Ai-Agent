@echo off
title LUMINO INTELLIGENCE
color 0B
cls

echo.
echo  [+] Initializing Environment...

:: Pindah ke folder script
cd /d "%~dp0"

:: Set Encoding agar support emoji/unicode
set PYTHONIOENCODING=utf-8

:: Jalankan main.py
python main.py

:: Jika error, jangan langsung tutup layar
pause