# PeopleFind

[![CI](https://github.com/zed1kgit/PeopleFind/actions/workflows/ci.yml/badge.svg)](https://github.com/zed1kgit/PeopleFind/actions/workflows/ci.yml)

**PeopleFind** это веб-приложение на Django для поиска людей по интересам. Вы подписываетесь на интересы, сайт
подбирает людей с общими увлечениями (чем больше общих интересов, тем выше шанс встретить человека), а при взаимном
одобрении обоим приходит уведомление с контактами.

<!-- Добавьте сюда скриншоты или GIF поиска, например: ![Поиск людей](docs/search.gif) -->

## Возможности

- Регистрация с подтверждением почты, вход по email, роли (пользователь, модератор, администратор).
- Интересы: подписка, участники, комментарии и топики с обсуждениями.
- Подбор людей с общими интересами: одобрить или отклонить; при взаимном одобрении приходит уведомление
  (и, если включено, письмо).
- Фоновые задачи на Celery (письма, уведомления), кэш и сессии в Redis.
- Адаптивная вёрстка (телефон, планшет, десктоп).

## Технологии

Python 3.10+, Django 5, PostgreSQL (SQLite для разработки), Redis, Celery, Bootstrap 5, WhiteNoise, gunicorn.

## Быстрый старт через Docker

```bash
cp .env_sample .env            # необязательно: значения по умолчанию подойдут для демо
docker compose up --build
```

Сайт откроется на <http://localhost:8000>. Docker поднимает сайт, PostgreSQL, Redis и Celery worker.
Демо-данные:

```bash
docker compose exec web python manage.py loaddata interests.json
docker compose exec web python manage.py ccsu             # администратор admin@example.com (пароль qwerty при DEBUG=1)
docker compose exec web python manage.py ccru --count 20  # случайные пользователи (пароль qwerty)
docker compose exec web python manage.py ccrtopics
docker compose exec web python manage.py ccrcomments
```

## Запуск без Docker

PostgreSQL и Redis не обязательны: без них проект использует SQLite, локальный кэш и выполняет задачи Celery сразу
в процессе сайта (письма при этом выводятся в консоль).

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env_sample .env             # DEBUG=1 уже включён

python manage.py migrate
python manage.py loaddata interests.json   # необязательно: базовые интересы
python manage.py ccsu                      # администратор
python manage.py runserver
```

Чтобы использовать PostgreSQL и Redis, заполните в `.env` переменные `POSTGRES_*` и `REDIS_URL`. Базу данных
можно создать командой `python manage.py ccdb`. При заданном `REDIS_URL` задачи выполняет воркер:

```bash
python manage.py runcelery      # или: celery -A PeopleFind worker -l info
```

## Настройки (переменные окружения)

| Переменная                             | Назначение                                                                  |
|----------------------------------------|-----------------------------------------------------------------------------|
| `DEBUG`                                | `1` для разработки. При `0` обязателен `SECRET_KEY`                          |
| `SECRET_KEY`                           | секретный ключ Django                                                        |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`| списки через запятую                                                         |
| `SITE_URL`                             | адрес сайта для ссылок в письмах                                             |
| `POSTGRES_DATABASE/USER/PASSWORD/HOST/PORT` | если `POSTGRES_DATABASE` пуст, используется SQLite                      |
| `REDIS_URL`                            | кэш, сессии и брокер Celery; если пуст, задачи выполняются сразу             |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT` | SMTP; без `EMAIL_HOST_USER` письма идут в консоль |
| `MUTUAL_EMAIL_ENABLED`                 | `1`: отправлять письмо при взаимном одобрении                                |
| `SERVE_MEDIA`, `SECURE_COOKIES`        | отдача медиа через Django и Secure-cookie                                    |

## Тесты и качество кода

```bash
python manage.py test
ruff check .
```

Те же проверки запускает GitHub Actions на каждый пуш. Миграции хранятся в репозитории: после изменения моделей
выполните `python manage.py makemigrations` и закоммитьте результат (CI проверяет это командой
`makemigrations --check`). Для проверок перед коммитом можно установить `pre-commit install`.

## Команды для тестовых данных

- `ccsu [--email ... --password ...]`: администратор (пароль из `--password`, `ADMIN_PASSWORD` или `qwerty` при DEBUG).
- `ccru --count 5`: случайные пользователи со случайными интересами (только при `DEBUG=1`, пароль `qwerty`).
- `ccrtopics --count 10 [--user_id N] [--interest_id N]`: случайные топики.
- `ccrcomments --count 10 [--user_id N] [--interest_id N | --topic_id N]`: случайные комментарии.

## Структура проекта

```
PeopleFind/   настройки, URL, Celery
users/        пользователи, регистрация и подтверждение почты, уведомления, задачи Celery
Interests/    интересы, подписки, подбор людей
topics/       топики и комментарии
templates/    шаблоны, static/ стили и скрипты (без jQuery)
```

## Планы

- REST API (Django REST Framework) и документация OpenAPI
- Личные сообщения между пользователями со взаимным одобрением
- Ограничение частоты запросов на вход и регистрацию
- Настройки приватности профиля, жалобы и блокировки

## Лицензия

[MIT](LICENSE)
