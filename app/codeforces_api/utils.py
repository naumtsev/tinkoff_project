import typing

import requests

from app import config

params = {'lang': 'en'}


def get_users_info(handles: typing.List[str]) -> typing.List[typing.Any]:
    args = '?handles=' + ';'.join(handles)
    req_url = config.CODEFORCES_API_URL.format('user.info') + args

    try:
        return requests.get(req_url, params=params).json()['result']
    except BaseException:
        return []


def get_user_submissions(handle: str) -> typing.List[typing.Any]:
    args = f'?handle={handle}'

    req_url = config.CODEFORCES_API_URL.format('user.status') + args
    try:
        return requests.get(req_url, params=params).json()['result']
    except BaseException:
        return []


def get_contest_problems(contest_id: str) -> typing.List[typing.Any]:
    args = f'?contestId={contest_id}&from=1&count=1'
    req_url = config.CODEFORCES_API_URL.format('contest.standings') + args
    try:
        return requests.get(req_url, params=params).json()['result']['problems']
    except BaseException:
        return []
