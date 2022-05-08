import typing

import requests

from app import config


def get_users_info(handles: typing.List[str]):
    req_url = config.CODEFORCES_API_URL.format('user.info') + '?handles={}'.format(
        ';'.join(handles)
    )
    try:
        return requests.get(req_url).json()['result']
    except BaseException:
        return []


def get_user_submissions(handle: str):
    req_url = config.CODEFORCES_API_URL.format('user.status') + f'?handle={handle}'
    try:
        return requests.get(req_url).json()
    except BaseException:
        return []


def get_contest_problems(contest_id: str):
    req_url = (
        config.CODEFORCES_API_URL.format('contest.standings')
        + f'?contestId={contest_id}&from=1&count=1'
    )
    try:
        return requests.get(req_url).json()['result']['problems']
    except BaseException:
        return []
