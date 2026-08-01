# Payment Operation Service

Сервис проведения платежных операций через внешнего провайдера с гарантией
корректного состояния при повторах, конкурентных запросах, потерянных
HTTP-ответах и перезапусках.

## Стек

- Python 3.14, FastAPI
- PostgreSQL, SQLAlchemy (async), Alembic (миграции)
- httpx (асинхронный HTTP-клиент к провайдеру)
- Docker + Docker Compose
- pytest, pytest-asyncio

### Таблицы

- **operation** - информация об операции;
- **operation_event** - неизменяемый журнал переходов и фактов
  (создание, отправка, применение квитанции, дубли/конфликты
  и пр.), доступен через `GET /operations/{id}/events`;
- **receipt_record** - лог каждой входящей callback-квитанции, включая
  дубликаты и конфликтующие;
- **provider_attempt** - лог каждого исходящего вызова провайдера (попытка,
  исход, HTTP-статус) - для retry-логики и диагностики.

### Ключевые решения корректности

- Переход `CREATED -> PROCESSING` выполняется одной атомарной операцией -
при конкурентных `submit` ровно один запрос создает намерение, остальные получают уже сохраненное состояние;
- Транзакция с БД никогда не удерживается на время внешнего HTTP-вызова -
  вызов провайдера выполняется вне блокировки, чтобы callback мог быть
  обработан независимо и без задержек;
- Обработка callback-квитанции и изменение статуса операции выполняются в
  одной транзакции; результат HTTP-ответа провайдера
не переводит операцию в финальный статус;
- При старте сервис находит операции в `PROCESSING` и возобновляет их отправку.

## Запуск

Требуется Docker и Docker Compose. Клонирование репозитория, создание .env и запуск из корня проекта.

Необходимо создать `.env` и скопировать туда все, что находится в файле `.env.template` (или ниже отсюда).

### Переменные окружения

```
APP_CONFIG__DB__USER=postgres
APP_CONFIG__DB__PASSWORD=postgres
APP_CONFIG__DB__NAME=fintech_db
APP_CONFIG__DB__HOST=localhost
APP_CONFIG__DB__PORT=5432
APP_CONFIG__ENV__ENVIRONMENT=prod
APP_CONFIG__ENV__LOGGING_LEVEL=info
APP_CONFIG__PROVIDER__URL=http://provider-simulator:8081

TEST__APP_CONFIG__DB__NAME=test_name
TEST__APP_CONFIG__DB__USER=test_user
TEST__APP_CONFIG__DB__PASSWORD=test_password
TEST__APP_CONFIG__DB__HOST=localhost
TEST__APP_CONFIG__DB__PORT=5433
```

`APP_CONFIG__ENV__ENVIRONMENT` - prod или dev (production/development)

`APP_CONFIG__ENV__LOGGING_LEVEL` - info или debug (уровень логирования)

`APP_CONFIG__PROVIDER__URL` - URL внешнего провайдера

Все остальные переменные являются настройками доступа к базе данных.
Переменные с префиксом `TEST` будут применяться для тестовой базы данных.

Непосредственно запуск приложения из корня проекта производится командой:

```
docker compose up --build
```

Идет поднятие БД, собираются `candidate-service` и `provider-simulator`.

Сервис поднимется на `http://localhost:8080`, провайдер-симулятор — на
`http://localhost:8081`. Миграции применяются автоматически при старте
контейнера (`alembic upgrade head` внутри entrypoint).

## Обработка граничных случаев

| Сценарий                                        | Поведение                                                                                                           |
|-------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Конкурентные `submit` одной операции            | Ровно один переход в `PROCESSING`, остальные получают текущее состояние                                             |
| Сетевая ошибка / `503` при вызове провайдера    | Ограниченный retry с экспоненциальным backoff и jitter; операция остаётся `PROCESSING`                              |
| Callback приходит раньше HTTP-ответа провайдера | `providerPaymentId` устанавливается из квитанции; поздний ответ провайдера игнорируется, если операция уже финальна |
| Повторная квитанция                             | `204`, новый переход не создается                                                                                   |
| Поздняя квитанция с противоположным результатом | `204`, фиксируется как проигнорированная, финальный статус не меняется                                              |
| Несовпадающий `providerPaymentId`               | `409 Conflict`                                                                                                      |
| Перезапуск сервиса во время `PROCESSING`        | При старте отправка возобновляется с тем же `Idempotency-Key`                                                       |

## Полный сквозной сценарий

```
curl http://localhost:8080/health
# {"status": "ok"}
```

```
curl -X POST http://localhost:8080/operations \
  -H "Content-Type: application/json" \
  -d '{
    "operationId": "op-123",
    "amount": "1000.00",
    "currency": "RUB",
    "description": "Оплата заказа"
  }'

# 201 created
```

```
curl -X POST http://localhost:8080/operations/op-123/submit

# 202 Accepted, status: PROCESSING
```

Callback-квитанция отправляется провайдером автоматически

```
curl -X POST http://localhost:8080/receipts \
  -H "Content-Type: application/json" \
  -d '{
    "providerPaymentId": "pay-123",
    "operationId": "op-123",
    "result": "COMPLETED",
    "message": "Payment completed",
    "occurredAt": "2026-07-07T12:00:00Z"
  }'

# 204 No Content
```

Проверка финального статуса:

```
curl http://localhost:8080/operations/op-123
```

Ожидаемый ответ: status: `COMPLETED`, `providerPaymentId` заполнен.

Повторный submit

```
curl -X POST http://localhost:8080/operations/op-123/submit

# 200 OK, статус не меняется
```

## Тесты

Для запуска тестов требуется установка зависимостей и поднятие тестовой базы данных.

```
python -m venv .venv
source .venv/bin/activate
# or .venv\Scripts\activate (on Windows)
```

```
pip install -e ".[dev]"
```

Из корня проекта:

```
docker compose -f docker-compose.test.yml up --build
pytest
```

Покрытие включает: атомарность конкурентных `submit`, обработку квитанции до
получения ответа провайдера, дублирующие/конфликтующие квитанции, recovery
после перезапуска.
