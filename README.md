# diplom
Это моя дипломная работа, но она до конца не завершена. Остаётся сделать фронтенд и я над ним уже работаю и даже есть эскизы, но выкладывать я их не стал.

# Инструкция по запуску проекта NeDis

##  Описание проекта

**NeDis** — это современная коммуникационная платформа, объединяющая функции:
-  Текстовые каналы для группового общения
-  Личные диалоги с end-to-end шифрованием
-  Видеозвонки через WebRTC
-  Безопасная аутентификация с JWT токенами


## Требования к системе

### Обязательные требования:
- **Python 3.8+** (рекомендуется Python 3.9+)
- **pip** (менеджер пакетов Python)
- **Git** (для клонирования репозитория)

### Рекомендуемые требования:
- **4 GB RAM** (для комфортной работы)
- **1 GB свободного места** на диске
- **Интернет-соединение** (для установки зависимостей)

## 📁 Структура проекта

```
NeDis/
├── app/
│   ├── main.py              # Основное FastAPI приложение
│   ├── database.py          # Настройка AsyncSession SQLAlchemy
│   ├── models.py            # Модели данных
│   ├── schemas.py           # Pydantic схемы
│   ├── utils.py             # JWT и хеширование паролей
│   ├── crud.py              # CRUD операции
│   └── routers/
│       ├── auth.py          # Аутентификация
│       ├── users.py         # Управление пользователями
│       ├── chat.py          # API для каналов
│       ├── chat_ws.py       # WebSocket чат
│       ├── direct.py        # Личные диалоги
│       ├── ws_direct.py     # WebSocket личные сообщения
│       └── webrtc.py        # WebRTC видеозвонки
│
├── templates/
│   └── direct_chat(1).html  # Основной HTML-файл
│
├── req.txt                  # Зависимости Python
└── README.md                # Документация
```

## 🔧 Установка и настройка

### Шаг 1: Клонирование проекта
```bash
git clone https://github.com/omarovsky/diplom.git
cd diplom
```

### Шаг 2: Создание виртуального окружения

**Windows:**
```cmd
python -m .venv venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Шаг 3: Установка зависимостей
```bash
pip install -r req.txt
```

### Шаг 4: Настройка базы данных
База данных SQLite создается автоматически при первом запуске.
Файл базы данных: `discord.db`

## 🚀 Запуск проекта


### Способ 1: Прямой запуск через uvicorn
```bash
uvicorn app.main:app --reload
```

### Способ 2: Скрипты автозапуска

**Windows:**
```cmd
start_windows.bat
```

## 🌐 Доступ к приложению

После успешного запуска:

- **Заходим через HTML файл** diplom\templates\direct_chat(1).html
- **Swagger UI (API swagger):** http://localhost:8000/docs
- **ReDoc (альтернативный  swagger):** http://localhost:8000/redoc

## 📱 Тестирование функций

### 1. Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "securepassword123"
  }'
```

### 2. Авторизация
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword123"
```

### 3. Создание канала
```bash
curl -X POST "http://localhost:8000/chat/channels" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name": "general"}'
```

## 🔧 Конфигурация

### Настройка JWT токенов
В файле `app/utils.py` можно изменить:
- `SECRET_KEY` — секретный ключ для JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES` — время жизни токена


### Настройка базы данных
В файле `app/database.py` можно изменить:
```python
DATABASE_URL = "sqlite+aiosqlite:///./discord.db"
```

## 🚫 Решение проблем

### Ошибка: "ModuleNotFoundError"
```bash
pip install --upgrade pip
pip install -r req.txt
```

### Ошибка: "Port already in use"
```bash
# Найти процесс использующий порт 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Запустить на другом порту
uvicorn app.main:app --port 8001 --reload
```

### Ошибка: "Database locked"
```bash
# Остановить все процессы приложения
# Удалить файл discord.db
# Перезапустить приложение
```


## Мониторинг

### Логи приложения
Логи выводятся в консоль. Для продакшена настройте:
```bash
uvicorn app.main:app --log-level info --access-log
```

### Проверка состояния
```bash
curl http://localhost:8000/docs
```

## Разработка

### Запуск в режиме разработки
```bash
uvicorn app.main:app --reload --log-level debug
```

### Форматирование кода
```bash
pip install black isort
black app/
isort app/
```


## Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки брандмауэра
4. Создайте issue в репозитории проекта

---

**Версия инструкции:** 0.1v  
**Дата обновления:** 15 июня 2025  
**Автор:** Омаров Абдулла Эльманович
