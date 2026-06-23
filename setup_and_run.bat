@echo off
REM Make a trip - one-command setup & run (Windows)
cd /d "%~dp0"

if not exist "venv" (
  echo Creating virtual environment...
  python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

echo Applying database migrations...
python manage.py migrate

if not exist ".seeded" (
  set /p yn="Load demo data (a sample hotel, bus, car, package, admin & customer login)? [Y/n] "
  if /I not "%yn%"=="n" (
    python manage.py shell < scripts\seed_data.py
    echo done > .seeded
  )
)

echo.
echo Starting the dev server at http://127.0.0.1:8000/
echo Press CTRL+C to stop.
python manage.py runserver
