@echo off
echo Запуск NeDis сервера...
echo.

:: Проверяем наличие виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv .venv
)

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Устанавливаем зависимости
echo Установка зависимостей...
pip install -r req.txt

:: Запускаем сервер
echo.
echo Запуск FastAPI сервера на http://localhost:8000
echo Для остановки нажмите Ctrl+C
echo.
uvicorn app.main:app --reload

pause
