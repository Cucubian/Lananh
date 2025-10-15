@echo off
echo ================================================
echo Website Quan ly San Cau Long - Setup Script
echo ================================================
echo.

echo [1/5] Kiem tra Python...
python --version
if errorlevel 1 (
    echo ERROR: Python khong duoc cai dat!
    pause
    exit /b 1
)
echo.

echo [2/5] Cai dat dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Khong the cai dat dependencies!
    pause
    exit /b 1
)
echo.

echo [3/5] Chay migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration that bai!
    pause
    exit /b 1
)
echo.

echo [4/5] Tao superuser (admin)...
echo Vui long nhap thong tin admin:
python manage.py createsuperuser
echo.

echo [5/5] Khoi dong server...
echo.
echo ================================================
echo Setup thanh cong!
echo.
echo Truy cap website tai: http://127.0.0.1:8000
echo Truy cap admin tai: http://127.0.0.1:8000/admin
echo ================================================
echo.
python manage.py runserver
