# Codeforces Problemsets Manager
 
Веб-приложение для организации мониторинга решения задач на codeforces.
Может использоваться в кружках/лагерях по спортивному программированию для составления контестов (подборок задач). 

### Основной функционал:
1) Создать/редактировать подборку задач 
2) Добавить пользователя codeforces в участники 
3) Просмотр результатов определённой подборки задач
4) Управлять видимостью участиков в контестах (PARTICIPANT - активный участник / SPECTATOR - скрытый участник)

### Описание сущностей:
    class User:           # Пользователь
        handle            # login на codeforces 
        rank              # ранг участника: newbie, pupil, specialist, expert...
        user_type         # тип участника: PARTICIPANT/SPECTATOR
        submissions       # посылки решений задач 
    
    class Problem:        # Задача
        title             # Название задачи
        contest_id        # Номер контеста на codefroces, в котором задача была создана
        problem_index     # Идентификатор задачи в контесте
        rating            # Число - сложность задачи
        problemsets       # Ссылки на подборки задач, в которых присутствует задача
    
    class Problemset:     # Подборка задач
        title             # Название подборки
        description       # Описание подборки
        image             # Изображение для подборки задач base64
        problems          # Ссылки на задачи в подборке
    
    class Submission:     # Посылка пользователя
        cf_id             # Глобальный номер посылки на codeforces 
        author_handle     # хэндл автора посылки
        verdict           # Вердикт OK/FAILED 
        creation_time     # Время отправки решения 
        contest_id, 
        problem_index     # Идентификатор задачи посылки  

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