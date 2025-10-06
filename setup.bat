@echo off
echo NFL Prediction Agent - Quick Setup
echo ===================================

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating data directories...
if not exist "data" mkdir data
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs

echo.
echo Initializing database...
python scripts\init_database.py

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Run: python scripts\collect_data.py --start-year 2020 --end-year 2024
echo 2. Run: python scripts\train_models.py
echo 3. Run: python main.py
echo.
echo Or simply run: python main.py and use the interactive menu
echo.
pause