@echo off
chcp 65001 > nul
title КухниМастер - Запуск сайта

echo ========================================
echo    КухниМастер - Запуск сайта
echo ========================================
echo.

:: Переходим в папку с батником
cd /d "%~dp0"

:: ШАГ 1 - Проверяем Python
echo [1/5] Проверяю Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo Python не найден. Скачиваю Python 3.12...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile 'python_installer.exe'"
    if errorlevel 1 (
        echo ОШИБКА: Не удалось скачать Python. Проверьте интернет-соединение.
        pause
        exit /b 1
    )
    echo Устанавливаю Python 3.12...
    python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    echo Удаляю установщик...
    del python_installer.exe
    echo Python установлен! Перезапустите start.bat
    pause
    exit /b 0
) else (
    echo Python найден - OK
)

:: ШАГ 2 - Создаём venv
if not exist "venv\Scripts\python.exe" (
    echo [2/5] Создаю виртуальное окружение...
    python -m venv venv
    echo OK
) else (
    echo [2/5] Виртуальное окружение уже есть - OK
)

:: ШАГ 3 - Устанавливаем зависимости
echo [3/5] Устанавливаю зависимости...
venv\Scripts\python.exe -m pip install django pillow --quiet
echo OK

:: ШАГ 4 - Миграции
echo [4/5] Применяю миграции базы данных...
venv\Scripts\python.exe manage.py migrate --run-syncdb
echo OK

:: ШАГ 5 - Запуск
echo [5/5] Запускаю сервер...
echo.
echo ========================================
echo  Сайт доступен по адресу:
echo  http://127.0.0.1:8000/
echo  Админка: http://127.0.0.1:8000/admin/
echo  Логин: admin  Пароль: admin123
echo  Для остановки нажмите Ctrl+C
echo ========================================
echo.

venv\Scripts\python.exe manage.py runserver

pause
