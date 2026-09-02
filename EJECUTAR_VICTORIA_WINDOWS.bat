@echo off
setlocal
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Creando entorno virtual...
  py -3 -m venv venv
  if errorlevel 1 python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERROR: No se pudieron instalar las dependencias.
  pause
  exit /b 1
)
python -m uvicorn main:app --reload
