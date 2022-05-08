import base64
import typing

from flask import Flask, render_template, request

from app import config, models
from app.db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY


@app.route('/', methods=['GET'])
def index() -> typing.Any:
    return 'OK'


@app.route('/add/<user>', methods=['GET'])
def add_user(user) -> typing.Any:
    db.add_user(user)
    return 'OK'


@app.route('/users', methods=['GET'])
def users_get() -> typing.Any:
    with db.create_session() as session:
        users = session.query(models.User).all()
        session.expunge_all()
        return render_template('users.html', users=users)


@app.route('/create-problemset', methods=['GET', 'POST'])
def create_problemset():
    if request.method == 'GET':
        return render_template('create_problemset.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        problems_strs = request.form.get('problems').split()
        image = request.files['image']
        image_base64 = base64.b64encode(image.stream.read())

        problems = []

        for problem_str in problems_strs:
            contest_id = None
            problem_index = None

            for j in range(len(problem_str)):
                if not problem_str[j].isdigit():
                    contest_id = problem_str[0:j]
                    problem_index = problem_str[j:]
                    break
            problems.append((contest_id, problem_index))

        status = db.add_problemset(title, description, problems, image_base64)
        return str(status)
