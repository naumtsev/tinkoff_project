import typing

from flask import Flask, redirect, render_template, session

from app import config, models, workers
from app.blueprints import actions_blueprint, problemset_blueprint, users_blueprint
from app.db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

app.register_blueprint(problemset_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(actions_blueprint)

workers.workers_scheduler.start()


@app.route('/', methods=['GET'])
def index() -> typing.Any:
    message = session.get('message', '')
    session['message'] = ''

    with db.create_session() as db_session:
        problemsets = db_session.query(models.Problemset).all()
        db_session.expunge_all()
        return render_template('index.html', problemsets=problemsets, message=message)


@app.errorhandler(404)
def page_not_found(_: typing.Any) -> typing.Any:
    session['message'] = '404 Page Not Found'
    return redirect('/')
