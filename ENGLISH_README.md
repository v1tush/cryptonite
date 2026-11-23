# Cryptonite

[Русская версия](README.md)

Cryptonite is a Django app where users publish and solve ciphers. It started as a team project for Yandex Lyceum. This iteration focuses on making the existing game more reliable: attempt limits, rewards, hint purchases, and moderation. Courses are still partially implemented.

**Stack:** Python 3.13, Django 5.2 LTS, PostgreSQL 16, APScheduler, Pillow, and Segno. uv manages dependencies, and Ruff handles linting and formatting.

## Quick start and demo

From the repository root, with Docker running:

```bash
docker compose up --build --wait
docker compose exec web python manage.py seed_demo
docker compose exec web python manage.py run_scheduler --once
```

Open <http://127.0.0.1:8000/>. The web app and scheduler start after migrations succeed. `/healthz/` checks the PostgreSQL connection, and `docker compose ps` shows service status. The database and media files are stored in named volumes. This Compose setup is **for local development only**: the web app binds to localhost, and the database port is not published.

### Two-minute walkthrough

1. Sign in as `demo_player` with the password `Cryptonite-demo-only!42`. Open the Caesar cipher demo («Демо: шифр Цезаря») from the home page, the library, or the URL path printed by `seed_demo`.
2. Buy the hint for 100 coins. Your balance drops to **0**, and the hint remains visible after a page refresh.
3. Submit `wrong` to use one of your two attempts. Then submit `HELLO WORLD`: you earn **100 XP and 25 coins**, and the solution scores **100 points**. Refreshing the page does not award them again.

`seed_demo` only runs in debug mode. Running it again does not reset balances, purchases, or attempts. Do not use the demo accounts on a public deployment.

## Run without Docker

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (CI and Docker use version `0.12.24`) and set up a local PostgreSQL database. From the repository root, choose one of these commands:

```bash
uv sync --locked           # application and dev dependencies (Ruff)
uv sync --locked --no-dev  # application dependencies only
```

uv reads `.python-version`, uses Python 3.13, and creates `.venv`. There is no need to activate it manually. `uv.lock` pins the resolved versions. Docker installs only the application dependencies. If you skipped the dev dependencies, use `uv run --locked --no-dev` instead of `uv run` to keep Ruff out of that environment.

Copy `.env.template` to `.env` (`Copy-Item .env.template .env` in PowerShell or `cp .env.template .env` in Bash). Set your database credentials and keep `DJANGO_DEBUG=True` for local HTTP. Django reads `.env` through `django-environ`; environment variables already set in the process take precedence.

```bash
cd cryptonite
uv run python manage.py migrate
uv run python manage.py seed_demo          # optional
uv run python manage.py createsuperuser    # optional, for /admin/
uv run python manage.py runserver
```

## Tests and CI

Run Ruff from the repository root:

```bash
uv run ruff check
uv run ruff format --check
```

Run Django checks from the **inner** `cryptonite/` directory, where `manage.py` lives:

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test --noinput
```

The PostgreSQL role needs `CREATEDB` for the standard test runner, or access to a pre-created test database. Tests cover attempt limits, repeated submissions and purchases, rollbacks, edit and moderation permissions, image uploads, and the scheduler. Concurrency tests use `TransactionTestCase` with separate PostgreSQL connections to verify that rewards are credited once, attempts stay within the limit, a balance cannot be spent twice, and two players can buy hints from each other without deadlocking.

GitHub Actions runs on pushes and pull requests. It checks Ruff, migrations, production settings, the PostgreSQL test suite, and whether the Compose stack starts. It does not deploy the app.

### How the game logic works

- [`ciphers/services.py`](cryptonite/ciphers/services.py) checks the attempt limit, records the solution, and updates XP, coins, and the solved-cipher count in a single transaction. Locking the cipher row works even on the first attempt, when there is no attempt record to lock. The trade-off is that concurrent operations on the same cipher run one at a time.
- A hint purchase is tied to a specific published cipher. The buyer's and author's wallet rows are locked in user ID order to avoid deadlocks when two players buy from each other. The transfer and the purchase record commit or roll back together. Editing a hint preserves its ID and existing purchases.
- [`users/fields.py`](cryptonite/users/fields.py) checks the detected format, file size, and dimensions of avatars and profile backgrounds. It accepts JPEG and PNG, decodes the image, and re-encodes it without the original metadata.

## Scheduler

The web process does not start the scheduler. Compose starts it automatically as a separate service after migrations succeed (`docker compose logs scheduler`). Without Docker, run one separate scheduler process under a service manager:

```bash
uv run python manage.py run_scheduler
```

At startup and every 15 minutes, including midnight in Django's `TIME_ZONE` (currently UTC), the scheduler checks whether a daily cipher has been selected. A database constraint enforces one selection per date, and restarts preserve the selection history. Once all published ciphers have been used, the scheduler picks the one that was featured least recently. `run_scheduler --once` checks once and exits.

## Public deployment

The local Compose setup and Django's `runserver` are not intended for public deployment. Set `DJANGO_DEBUG=False`, use your own PostgreSQL credentials, list explicit `DJANGO_ALLOWED_HOSTS` without `*`, and generate a unique `DJANGO_SECRET_KEY`:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(64))"
uv run python manage.py check --deploy
```

Production enables HTTPS redirects and secure cookies. Set `DJANGO_TRUST_PROXY_SSL_HEADER=True` only if a trusted proxy sets `X-Forwarded-Proto` itself and strips any client-supplied value. If needed, configure `DJANGO_CSRF_TRUSTED_ORIGINS` with full `https://` origins. Set `DJANGO_HSTS_SECONDS` after verifying HTTPS; only enable `DJANGO_HSTS_INCLUDE_SUBDOMAINS` and `DJANGO_HSTS_PRELOAD` if all subdomains are ready for those policies.

Apply migrations, run `collectstatic`, and use a WSGI or ASGI server. Serve uploads from a separate domain that does not receive the app's cookies, and set a request body limit on the proxy (for example, 8 MiB). Configure the media URL with `DJANGO_MEDIA_URL`.

## Project credits

The original app was built as a team project. This iteration adds transactional gameplay, stricter access and upload checks, PostgreSQL tests, a local Docker setup, CI, and a repeatable demo. Historical rewards were not recalculated. See [`ER.png`](ER.png) for the database schema.
