# URL Shortener Service

Сервис для сокращения ссылок.

## Технологии

- **FastAPI** — высокопроизводительный веб-фреймворк
- **PostgreSQL** — основная база данных
- **Redis** — кэширование популярных ссылок
- **SQLAlchemy** — ORM для работы с БД
- **Alembic** — миграции
- **FastAPI Users** — аутентификация и авторизация
- **Docker** — контейнеризация

## Функционал

- Создание коротких ссылок (случайные или свои)
- Авторизация через JWT
- Статистика переходов
- Установка срока действия ссылок
- Автоматическая деактивация просроченных ссылок
- Кэширование популярных ссылок в Redis
- REST API с документацией Swagger

## Структура проекта

        fastapi-project/
        ├── src/
        │ ├── auth/ # Аутентификация (fastapi-users)
        │ ├── models/ # SQLAlchemy модели
        │ ├── routers/ # Эндпоинты API
        │ ├── schemas/ # Pydantic схемы
        │ ├── utils/ # Вспомогательные функции
        │ ├── config.py # Конфиг
        │ ├── database.py/ # Подключение к бд
        │ ├── main.py # Запуск приложения
        │ ├── redis.py # Подключение к redis 
        │ ├── workers.py # Периодические задачи
        ├── migrations/ # Миграции Alembic
        ├── docker-compose.yml # Локальный запуск всех сервисов
        ├── Dockerfile # Сборка приложения
        └── requirements.txt # Зависимости

## Примеры запросов

1. Регистрация пользователя (PUT /auth/register)

        curl -X 'POST' \
        'https://url-shorten-qxwq.onrender.com/auth/register' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "email": "admin@1.com",
        "password": "123",
        "is_active": true,
        "is_superuser": true,
        "is_verified": false
        }'

2. Создание короткой ссылки (PUT /links/shorten):

        curl -X 'POST' \
        'https://url-shorten-qxwq.onrender.com/links/shorten' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "custom_alias": "test-link",
        "expires_at": "2026-03-16T17:39:05+03:00",
        "original_url": "https://test.com"
        }'

        В этом эндпоинте проверяется статус пользователя. По умолчанию для анонима, обычного пользователя и админа стоит (соответственно) 7, 30 и 90 дней на истечение ссылки. А максимальный срок годности ссылки - 7, 100 и 365 дней.
        При этом по истечении времени ссылка не удаяется в базе данных, а лишь помечается как просроченная. Пока что ссылка вообще не удаляется из базы данных никак кроме как через использование эндпоинта DELETE /links/{short_code}. Это сделано для того, чтобы легко можно было отслеживать историю "удаленных" ссылок.


3. Переход по короткой ссылке (GET /links/{short_code}):

    
        curl -X 'GET' \
        'https://url-shorten-qxwq.onrender.com/links/test-link' \
        -H 'accept: application/json'


4. Поиск коротких ссылок ведущих на URL (GET /links/search)

        curl -X 'GET' \
        'https://url-shorten-qxwq.onrender.com/links/search?original_url=test.com&exact_match=false' \
        -H 'accept: application/json'

        Пример ответа: 
        [
            {
                "short_code": "test-link",
                "original_url": "https://test.com/"
            }
        ]


5. Получение всех своих ссылок (GET /links/my)

        curl -X 'GET' \
        'https://url-shorten-qxwq.onrender.com/links/my?include_active=true&include_inactive=true' \
        -H 'accept: application/json' \
        -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MmE4OTcyYS1hY2I1LTQ4NDgtYjIzNy0yZjAyODBiZmMwODYiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc3MzA2ODQ0N30.h0MXQCITNAwqjTH2e7rD_s78eAYizg78rPAwVMqc2ps'

        Пример ответа:

        [
            {
                "original_url": "https://test.com/",
                "created_at": "2026-03-09T13:20:55.579870",
                "id": "93e4b305-1573-4329-91a4-0019977d5b4b",
                "last_use": null,
                "clicks": 0,
                "user_id": "42a8972a-acb5-4848-b237-2f0280bfc086",
                "short_code": "test1",
                "is_active": true,
                "updated_at": null,
                "expires_at": "2026-03-16T13:20:00"
            },
            {
                "original_url": "https://hahah.com/",
                "created_at": "2026-03-09T13:39:05.685765",
                "id": "04d57cd3-27b5-40ce-b243-b060600ee5a4",
                "last_use": null,
                "clicks": 3,
                "user_id": "42a8972a-acb5-4848-b237-2f0280bfc086",
                "short_code": "idk222",
                "is_active": false,
                "updated_at": null,
                "expires_at": "2026-03-09T14:03:00"
            }
        ]

        В этом эндпоинте можно посмотреть все свои ссылки (в том числе истекшие). 
        Это делается при помощи указания параметров поиска 
        include_active=true&include_inactive=true (по умолчанию они тоже включены).


6. Получение статистики ссылки (GET /links/{short_code}/stats)

        curl -X 'GET' \
        'https://url-shorten-qxwq.onrender.com/links/test1/stats' \
        -H 'accept: application/json'

        Пример ответа:
        {
        "short_code": "test1",
        "original_url": "https://test.com/",
        "clicks": 21,
        "is_active": true,
        "created_at": "2026-03-09T13:20:55.579870",
        "updated_at": null,
        "last_use": "2026-03-09T14:08:10"
        }


![Swagger UI](screenshots/swagger_links.png)

## Инструкция по запуску
Запуск через Docker

        git clone https://github.com/McChainiy/url_shorten
        cd url_shorten
        cp .env.example .env #настраиваем окружение для docker
        docker compose up --build


## Описание таблиц в БД

#### **Таблица `user`** (пользователи)

Хранит информацию о зарегистрированных пользователях. Наследуется от `SQLAlchemyBaseUserTableUUID` (fastapi-users).

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор пользователя | PRIMARY KEY |
| `email` | VARCHAR | Email пользователя | UNIQUE, NOT NULL |
| `hashed_password` | VARCHAR | Хеш пароля | NOT NULL |
| `is_active` | BOOLEAN | Активен ли аккаунт | DEFAULT true |
| `is_superuser` | BOOLEAN | Права администратора | DEFAULT false |
| `is_verified` | BOOLEAN | Подтвержден ли email | DEFAULT false |


#### **Таблица `links`** (короткие ссылки)

Основная таблица проекта. Хранит все созданные короткие ссылки и их статистику.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор ссылки | PRIMARY KEY |
| `original_url` | TEXT | Оригинальный длинный URL | NOT NULL |
| `short_code` | VARCHAR(20) | Короткий код для доступа | UNIQUE, NOT NULL, INDEX |
| `created_at` | TIMESTAMP | Дата создания ссылки | DEFAULT now() |
| `is_active` | BOOLEAN | Активна ли ссылка | DEFAULT true, NOT NULL |
| `last_use` | TIMESTAMP | Дата последнего перехода |  |
| `updated_at` | TIMESTAMP | Дата последнего обновления |  |
| `clicks` | INTEGER | Количество переходов | DEFAULT 0, NOT NULL |
| `expires_at` | TIMESTAMP | Дата истечения срока | |
| `user_id` | UUID | ID владельца ссылки | FOREIGN KEY (users.id) |



## Тесты

Все тесты находятся в папке tests

1) tests/unit
В этой директории собраны различные тесты, которые покрывают те функции, которые работают без обращения к API

2) tests/functional
В этой директории собраны тесты, которые покрывают обращения к определенным эндпоинтам.
Были созданы моки в файле conftest.py, а также переорпделены некоторые зависимости.

ВАЖНО: тесты из пункта 1, 2 можно проверить следующей командой

`python -m pytest --cov=src --cov-report html`

ИЛИ

`coverage run -m pytest tests`

Посмотреть результаты функционального и юнит-тестирования можно в директории htmlcov (запушил ее в гитхаб, т.к. вроде не слишком много весит)

3) tests/load
В этой директории содержится файл для нагрузочного тестирования. Для нагрузочного тестирования я создал отдельный docker-образ, в котором запускается бд и редис. 
Чтобы включить нагрузочное тестирование надо запустить скрипт `./load_tests.sh`, а затем перейти по ссылке http://localhost:8089


----


P.S. При создании тестов иногда обращался к генераивным моделям, в основном - ChatGPT и DeepSeek. Тем не менее, все функции и тесты понимаю и понимаю, что и как работает. Приходилось много дебажить и вдумываться. 