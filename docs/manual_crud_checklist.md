# Manual CRUD Checklist

Документ для ручной проверки API без изменения бизнес-логики.

## 1) Предусловия

1. Активировано окружение: `source venv/bin/activate`.
2. Применены миграции: `alembic upgrade head`.
3. Запущен API: `uvicorn app.main:app --reload`.
4. Базовый health-check:

```bash
curl http://127.0.0.1:8000/health
```

Ожидаемо: `{"status":"ok"}`.

## 2) Тестовые данные

Используйте уникальный префикс, например `crud_probe_20260502`.

- `telegram_id` owner: `920000001`
- `telegram_id` contact: `920000002`

## 3) Users CRUD

### 3.1 Create user (owner)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 920000001,
    "full_name": "crud_probe_owner",
    "username": "crud_probe_owner",
    "phone": "+992900000001",
    "role": "employer"
  }'
```

Ожидаемо: `200`, в ответе есть `id`.

### 3.2 Create user (contact)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 920000002,
    "full_name": "crud_probe_contact",
    "username": "crud_probe_contact",
    "phone": "+992900000002",
    "role": "employer"
  }'
```

Ожидаемо: `200`, в ответе есть `id`.

### 3.3 Read user

```bash
curl http://127.0.0.1:8000/api/v1/users/{owner_id}
```

Ожидаемо: `200`, корректные поля пользователя.

### 3.4 Update user

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/users/{owner_id} \
  -H "Content-Type: application/json" \
  -d '{"phone":"+992900001111"}'
```

Ожидаемо: `200`, телефон обновлён.

### 3.5 List users

```bash
curl "http://127.0.0.1:8000/api/v1/users?limit=20&offset=0"
```

Ожидаемо: `200`, список пользователей.

### 3.6 Negative: user not found

```bash
curl http://127.0.0.1:8000/api/v1/users/99999999
```

Ожидаемо: `404`, `{"detail":"User not found"}`.

## 4) Job Posts CRUD

### 4.1 Create job post

```bash
curl -X POST http://127.0.0.1:8000/api/v1/job-posts \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": {owner_id},
    "title": "crud_probe_job",
    "description": "crud_probe description long enough",
    "city": "Dushanbe",
    "job_type": "vacancy",
    "status": "draft",
    "contact_username": {contact_id}
  }'
```

Ожидаемо: `201`, есть `id` и статус `draft`.

### 4.2 Read job post

```bash
curl http://127.0.0.1:8000/api/v1/job-posts/{job_id}
```

Ожидаемо: `200`, возвращаются `user_name` и `contact_username`.

### 4.3 List job posts + filters

```bash
curl "http://127.0.0.1:8000/api/v1/job-posts?status=draft"
curl "http://127.0.0.1:8000/api/v1/job-posts?job_type=vacancy"
curl "http://127.0.0.1:8000/api/v1/job-posts?city=dushan"
```

Ожидаемо: `200`, фильтры применяются.

### 4.4 Update transitions (happy-path)

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} -H "Content-Type: application/json" -d '{"status":"pending"}'
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} -H "Content-Type: application/json" -d '{"status":"approved"}'
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} -H "Content-Type: application/json" -d '{"status":"published"}'
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} -H "Content-Type: application/json" -d '{"published_message_id":12345}'
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} -H "Content-Type: application/json" -d '{"status":"closed"}'
```

Ожидаемо: все ответы `200`.

### 4.5 Negative: invalid status transition

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} \
  -H "Content-Type: application/json" \
  -d '{"status":"approved"}'
```

Если текущий статус `draft`, ожидаемо: `400`, `Invalid status transition: draft → approved`.

### 4.6 Negative: published_message_id at wrong status

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} \
  -H "Content-Type: application/json" \
  -d '{"status":"pending","published_message_id":222}'
```

Ожидаемо: `400`, `published_message_id can be set only for published job posts`.

### 4.7 Negative: contact user not found

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/job-posts/{job_id} \
  -H "Content-Type: application/json" \
  -d '{"contact_username":99999999}'
```

Ожидаемо: `404`, `Contact user not found`.

### 4.8 Negative: job post not found

```bash
curl http://127.0.0.1:8000/api/v1/job-posts/99999999
```

Ожидаемо: `404`, `Job post not found`.

## 5) Проверка удаления и целостности

1. Удалить job post:

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/job-posts/{job_id}
```

Ожидаемо: `204`.

2. Удалить пользователей:

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/users/{contact_id}
curl -X DELETE http://127.0.0.1:8000/api/v1/users/{owner_id}
```

Ожидаемо: `204`.

3. Повторное чтение удалённых сущностей:

Ожидаемо: `404`.

## 6) Что подтверждает неизменность бизнес-логики

- Работают те же допустимые переходы статусов.
- Запрет `published_message_id` вне `published` сохраняется.
- Сообщения ошибок `User not found`, `Contact user not found`, `Job post not found` неизменны.
- Публичные маршруты API не изменены.
