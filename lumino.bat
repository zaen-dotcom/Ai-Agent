@echo off
title LUMINO SYSTEM
color 0B
cls

echo.
echo  LUMINO INTELLIGENCE SYSTEM
echo  Initializing...
echo.

:: Pindah ke folder script
cd /d "%~dp0"

:: Jalankan main.py langsung
python main.py

:: Jika error, jangan langsung tutup layar
pause