# CryptoNite — платформа для изучения шифров

![Pipeline Status](https://gitlab.crja72.ru/django/2025/autumn/course/students/197347-andreyovsandrey-course-1474/badges/main/pipeline.svg)

## ⚙️ Требования

Перед запуском проекта убедитесь, что у вас установлена необходимая версия Python: **3.10, 3.11, 3.12 или 3.13**, **git и gettext** 

---

## 🚀 Запуск проекта в режиме разработки

Следуйте шагам ниже, чтобы развернуть проект локально.

---

### 1. Клонирование репозитория

Скачайте проект на локальную машину и перейдите в его директорию:

```bash
git clone https://gitlab.crja72.ru/django/2025/autumn/course/projects/team-1.git
cd team-1
```

---

### 2. Создание и активация виртуального окружения

Создаём виртуальное окружение для Python и активируем его:

| ОС                          | Команды                                                 |
| :---------------------------- | :------------------------------------------------------------- |
| **Windows ❖**          | ``python -m venv venv`` ` && ` ``venv/Scripts/activate``     |
| **macOS  / Linux 🐧** | ``python3 -m venv venv`` ` && ` ``source venv/bin/activate`` |

---

### 3. Установка зависимостей

Зависимости проекта разделены на несколько файлов.
Выберите нужный вариант в зависимости от окружения.

#### 🔧 Для разработки (`dev.txt`)
``pip install -r requirements/dev.txt``

#### 🧪 Для тестирования (`test.txt`)
``pip install -r requirements/test.txt``

#### 🚀 Для продакшена (`prod.txt`)
``pip install -r requirements/prod.txt``

---

### 4. Настройка переменных окружения

Создайте файл `.env` на основе шаблона:

| Среда                     | Команда                   |
| :----------------------------- | :------------------------------- |
| Linux / macOS / Git Bash / WSL | `cp .env.template .env`        |
| Windows (PowerShell)           | `Copy-Item .env.template .env` |
| Windows (CMD)                  | `copy .env.template .env`      |

Пример содержимого `.env`:

```env
# Django Settings
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=fake_insecure_key_for_template_!@
DJANGO_LANGUAGE_CODE=ru

# Database Settings
DJANGO_DB_NAME=demo_project_db
DJANGO_DB_USER=demo_user
DJANGO_DB_PASSWORD=demo_password_123ABC
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
```

---

Перейдите в папку проекта:

```bash
cd cryptonite
```

### 5. Применение миграций и работа с базой данных

#### Выполните миграции

| ОС                | Команда                |
| :------------------ | :---------------------------- |
| Windows ❖          | `python manage.py migrate`  |
| macOS  / Linux 🐧 | `python3 manage.py migrate` |

#### Загрузка тестовых данных (фикстур)

Если проект содержит подготовленные фикстуры, загрузите их следующей командой:

| ОС        | Команда                                   |
| :---------- | :----------------------------------------------- |
| Все ОС | `python manage.py loaddata fixtures/data.json` |

*(Если файла фикстур нет, этот шаг можно пропустить.)*

---

### 6. Создание суперпользователя

Создайте администратора для доступа к админ-панели:

| ОС                | Команда                        |
| :------------------ | :------------------------------------ |
| Windows ❖          | `python manage.py createsuperuser`  |
| macOS  / Linux 🐧 | `python3 manage.py createsuperuser` |

После запуска сервера админка будет доступна по адресу:
👉 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

### 7. Локализация проекта

Выберите язык по умолчанию в файле `settings.py`:

```python
LANGUAGE_CODE = 'en'
```

Для генерации и компиляции переводов используйте:

| Действие                              | Команда                                                                 |
| :-------------------------------------------- | :----------------------------------------------------------------------------- |
| Создать файлы перевода    | `django-admin makemessages -l en` или `django-admin makemessages -l ru` |
| Скомпилировать переводы | `django-admin compilemessages`                                               |

---

### 8. Запуск сервера разработки

Теперь можно запустить проект:

| ОС                | Команда                  |
| :------------------ | :------------------------------ |
| Windows ❖          | `python manage.py runserver`  |
| macOS  / Linux 🐧 | `python3 manage.py runserver` |

После запуска проект будет доступен по адресу:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🗄️ ER-диаграмма базы данных

![ER-диаграмма базы данных](/ER.jpg)

> На диаграмме показана структура моделей проекта.
> Со временем база данных может расширяться, добавляться новые связи и таблицы.

---

© 2025 — Проект CriptoNite, Яндекс Лицей.
