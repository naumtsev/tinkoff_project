# Codeforces Problemsets Manager

Web-application 

### Описание:
    ...

### Создание окружения:
    make venv

### Запуск тестов:
    docker-compose run --rm app make test

### Запуск линтеров:
    make lint

### Запуск форматтеров:
    make format

### Запуск приложения:
    docker-compose up


Структура проекта:

```python
app
├── __init__.py
├── app.py              
├── blueprints          # разделение urls по логике работы 
│   ├── __init__.py
│   ├── actions.py
│   ├── problemset.py
│   └── users.py
├── codeforces_api     # методы, реализующие взаимодействие с codeforces API 
│   ├── __init__.py
│   └── utils.py
├── models             # классы, описывающие базу данных
│   ├── base.py
│   ├── __init__.py
│   ├── problemlink.py
│   ├── problem.py
│   ├── problemset.py
│   ├── submission.py
│   └── user.py
├── templates           # шаблоны для рендеринга при помощи jinja2
│   ├── create_or_update_problemset.html
│   ├── index.html
│   ├── problemset.html
│   └── users.html
├── config.py           # конфигурационный файл   
├── db.py               # класс, взаимодействующий с базой данных
├── utils.py            # вспомогательные функции
└── workers.py          # scheduler / workers, обновляющие актуальные данные с codeforces
```
Зависимости:
```python
[tool.poetry.dependencies]
python = "^3.9"
SQLAlchemy = "^1.4.36"
requests = "^2.27.1"
grequests = "^0.6.0"
Flask = "^2.1.2"
Pillow = "^9.1.0"
APScheduler = "^3.9.1"
Flask-Cache = "^0.13.1"
types-requests = "^2.27.25"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
pytest-cov = "^3.0.0"
autoflake = "^1.4"
isort = "^5.10.0"
black = "^22.1"
unify = "^0.5"
flake8 = "^4.0"
pylint = "^2.12.1"
mypy = "^0.940"
pytest-deadfixtures = "^2.2.1"
```