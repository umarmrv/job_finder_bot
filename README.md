# Job Finder Bot API

FastAPI API для работы с пользователями и объявлениями о работе (`job_posts`).

## Требования

- Python 3.12+
- PostgreSQL 14+

## Установка

```bash
git clone <your-repo-url>
cd job_finder_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Для Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка окружения

Создайте `.env` на основе шаблона:

```bash
cp .env.example .env
```

Пример `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/jobs_bot
```

## Миграции

Применить миграции:

```bash
alembic upgrade head
```

Откатить последнюю миграцию:

```bash
alembic downgrade -1
```

## Запуск API

```bash
uvicorn app.main:app --reload
```

Документация будет доступна по адресу:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Основные эндпоинты

### Users

- `POST /api/v1/users/`
- `GET /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

### Job posts

- `POST /api/v1/job-posts`
- `GET /api/v1/job-posts`
- `GET /api/v1/job-posts/{job_id}`
- `PATCH /api/v1/job-posts/{job_id}`
- `DELETE /api/v1/job-posts/{job_id}`

## Примеры CRUD-запросов

Создать пользователя:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 1000001,
    "full_name": "Ali Valiyev",
    "username": "ali_valiyev",
    "phone": "+992900000001",
    "role": "employer"
  }'
```

Создать объявление:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/job-posts \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "Santexnik kerak",
    "description": "Objektda doimiy ish, tajriba shart.",
    "city": "Dushanbe",
    "job_type": "vacancy",
    "status": "draft"
  }'
```

Обновить статус объявления:

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
```

Удалить объявление:

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/job-posts/1
```

## Типовые ошибки

- `404 Not Found`:
  - `User not found`
  - `Job post not found`
  - `Contact user not found`
- `400 Bad Request`:
  - `Invalid status transition: ...`
  - `published_message_id can be set only for published job posts`
- `422 Unprocessable Entity`:
  - ошибки валидации Pydantic (неверные типы/длины/диапазоны)

## Ручная проверка API

1. Запустите PostgreSQL и убедитесь, что база доступна по `DATABASE_URL`.
2. Выполните `alembic upgrade head`.
3. Запустите `uvicorn app.main:app --reload`.
4. Откройте `http://127.0.0.1:8000/docs`.
5. Проверьте сценарии:
   - создание пользователя;
   - создание job post;
   - перевод статусов `draft -> pending -> approved -> published -> closed`;
   - негативные проверки переходов и `published_message_id`.
