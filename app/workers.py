import typing

from app import codeforces_api, models
from app.db import db


def update_users_info():
    with db.create_session() as session:
        users = session.query(models.User).all()
        handles = []
        d_users: typing.Dict[str, models.User] = {}

        for user in users:
            handles.append(user.handle)
            d_users[user.handle] = user

        for user_info in codeforces_api.get_users_info(handles):
            handle = user_info['handle']
            rank = user_info['rank']
            d_users[handle].rank = models.Rank.from_str(rank)
