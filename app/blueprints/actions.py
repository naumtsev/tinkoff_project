import typing

from flask import Blueprint, redirect, session

from app import workers

actions_blueprint = Blueprint('actions', __name__)


@actions_blueprint.route('/update_users_submissions', methods=['GET'])
def update_users_submissions() -> typing.Any:
    workers.update_users_submissions()
    session['message'] = 'Users submissions updated'
    return redirect('/')


@actions_blueprint.route('/update_users_info', methods=['GET'])
def update_users_info() -> typing.Any:
    workers.update_users_info()
    session['message'] = 'Users info updated'
    return redirect('/')
