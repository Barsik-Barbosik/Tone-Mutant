@echo off
cd /d "%~dp0"
if not exist ".runtime\python312\Scripts\python.exe" (
    echo No se encuentra el entorno local. Consulta ACCESIBILIDAD.md.
    pause
    exit /b 1
)
".runtime\python312\Scripts\python.exe" main.py
if errorlevel 1 pause
