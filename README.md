# Cryptonite

Cryptonite is a Django web application for creating, solving, and sharing ciphers. It was built as a team project for the Yandex Lyceum project defense.

## Features

- User registration, login, profiles, and profile editing
- Community cipher creation, editing, moderation, and solving
- Difficulty levels, attempt limits, hints, and in-app rewards
- Likes, leaderboards, and achievement rules
- Daily cipher selection with history
- QR codes for ciphers
- Russian and English localization
- Course-related models and views (partially implemented)

## Tech stack

- Python 3.10–3.13
- Django 5.2
- PostgreSQL
- Pillow, Segno, APScheduler

## Requirements

- Python 3.10, 3.11, 3.12, or 3.13
- PostgreSQL
- Git
- `gettext` is needed only if you want to compile translation files

## Local development setup

Commands below start from the repository root.

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/v1tush/cryptonite.git
cd cryptonite
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
```

### 3. Configure the environment

Copy `.env.template` to `.env` in the repository root:

```powershell
# Windows PowerShell
Copy-Item .env.template .env
```

```bash
# macOS / Linux / Git Bash
cp .env.template .env
```

Set the database name, user, password, and host in `.env` to match a PostgreSQL database you have created. The template's values are examples for local development only. Generate a unique Django secret key for your local environment and keep `.env` private.

### 4. Apply migrations and create an admin account

The Django `manage.py` file is inside the `cryptonite/` directory:

```bash
cd cryptonite
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the web app

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The Django admin is at <http://127.0.0.1:8000/admin/>.

## Daily cipher scheduler

The daily cipher scheduler is a separate, long-running process; starting the Django web server does **not** start it. In a second terminal, activate the same virtual environment, go to the inner `cryptonite/` directory, and run:

```bash
python manage.py run_scheduler
```

Keep this process running while using the app. It selects an approved cipher immediately on startup, then schedules subsequent selections every 24 hours. If there are no approved ciphers, no daily cipher can be selected.

## Tests and code checks

The GitLab CI configuration runs Black, Flake8, and Django's test command. The repository currently has little to no automated application test coverage, so passing the test job should not be taken as proof that all user flows are covered.

## Translations

Translation sources are in `cryptonite/locale/`. To update translations, install `gettext` and run these commands from the inner `cryptonite/` directory:

```bash
python manage.py makemessages -l en
python manage.py makemessages -l ru
python manage.py compilemessages
```

## Project structure

```text
cryptonite/       Django project and apps
requirements/     Development, test, and production dependencies
ER.png            Entity-relationship diagram
```

This is an educational project and is not configured as a production deployment. Before deploying it publicly, review the Django secret key, allowed hosts, database credentials, HTTPS/security settings, media storage, and background scheduler deployment.
