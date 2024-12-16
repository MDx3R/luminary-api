# API

## Как запустить?

```bash
python manage.py runserver
```

### Переменные среды

Для конфигурации переменных среды следует создать файл .env в директории проекта.

- `DEBUG` - Флаг для включения (True) и выключения (False) debug-режима Django

- `DB_NAME` - Имя базы данных PostgreSQL
- `DB_USER` - Имя пользователя
- `DB_PASSWORD` - Пароль пользователя
- `DB_HOST` - Адрес для подключения
- `DB_PORT` - Порт для подключения

- `OPENAI_API_KEY` - Ключ API для модели
- `OPENAI_API_URL` - URL для API модели
- `MODEL_NAME` - Наименование модели (рекомендуется gpt-4o-mini)