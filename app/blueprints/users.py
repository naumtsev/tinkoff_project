import typing

from flask import Blueprint, redirect, render_template, request, session, url_for

from app import models
from app.db import db

users_blueprint = Blueprint('users', __name__)


class UserRow:
    def __init__(self, handle: str, rank: models.Rank, user_type: models.UserType):
        self.handle = handle
        self.handle_color = models.get_rank_color(rank)
        self.user_type = user_type


@users_blueprint.route('/users', methods=['GET'])
def users_get() -> typing.Any:
    with db.create_session() as db_session:
        users = db.get_users(
            [models.UserType.PARTICIPANT, models.UserType.SPECTATOR], db_session
        )
        db_session.expunge_all()
        users_rows = []

        for user in users:
            users_rows.append(UserRow(user.handle, user.rank, user.user_type))

        return render_template('users.html', users=users_rows, UserType=models.UserType)


@users_blueprint.route('/change_user_type/<handle>', methods=['POST'])
def change_user_type_post(handle: str) -> typing.Any:
    with db.create_session() as db_session:
        user = db.get_user_by_handle(handle, db_session)

        if user is None:
            session['message'] = 'User is not registered'
            return redirect(url_for('index'))

        new_user_type = int(
            request.form.get('user_type', models.UserType.PARTICIPANT.value)
        )

        user.user_type = models.UserType(new_user_type)
        return redirect('/users')


@users_blueprint.route('/add-user', methods=['POST'])
def add_user_post() -> typing.Any:
    handle = request.form['handle']
    ok = db.add_user(handle)
    if not ok:
        session[
            'message'
        ] = f'User with handle "{handle}" is not registered on Codeforces'
        return redirect('/')

    return redirect('/users')
