import json

from app import config, models, workers
from app.app import app
from app.db import db


def test_one_big_test(requests_mock):
    handle = 'Naumtsev'
    with app.test_client() as test_client:
        url_user_info = (
            config.CODEFORCES_API_URL.format('user.info') + '?handles=Naumtsev'
        )

        requests_mock.get(
            url_user_info,
            json={
                'status': 'OK',
                'result': [
                    {
                        'rating': 1838,
                        'handle': 'Naumtsev',
                        'rank': 'expert',
                        'maxRating': 1890,
                        'maxRank': 'expert',
                    }
                ],
            },
        )

        test_client.post('/add-user', data={'handle': handle})
        with db.create_session() as session:
            user = (
                session.query(models.User)
                .filter(models.User.handle == handle)
                .one_or_none()
            )
            assert user is not None
            assert user.handle == handle

        workers.update_users_info()
        with db.create_session() as session:
            user = (
                session.query(models.User)
                .filter(models.User.handle == handle)
                .one_or_none()
            )
            assert user is not None
            assert user.rank == models.Rank.EXPERT

        with open('tests/sources/submissions.txt', 'r', encoding='UTF-8') as file:
            data = json.load(file)
            url_user_submissions = (
                config.CODEFORCES_API_URL.format('user.status') + '?handle=Naumtsev'
            )
            requests_mock.get(url_user_submissions, json=data)
        workers.update_user_submissions('Naumtsev')
        workers.update_users_submissions()

        with db.create_session() as session:
            user = (
                session.query(models.User)
                .filter(models.User.handle == handle)
                .one_or_none()
            )

            assert user is not None

            subs = set()

            for sub in user.submissions:
                subs.add(sub.cf_id)

            assert subs == {150814933, 150814324, 150812833}

        with open('tests/sources/problems.txt', 'r', encoding='UTF-8') as file:
            data = json.load(file)
            url_problems = (
                config.CODEFORCES_API_URL.format('contest.standings')
                + '?contestId=1656&from=1&count=1'
            )
            requests_mock.get(url_problems, json=data)

        test_client.post(
            '/problemset',
            data={
                'title': 'test #1',
                'description': 'test description',
                'image': '',
                'problems': '1656A 1656B 1656C',
            },
        )

        with db.create_session() as session:
            problemsets = session.query(models.Problemset).all()
            assert len(problemsets) == 0
            users = db.get_users([models.UserType.PARTICIPANT], session)
            assert len(users) == 1
            assert users[0].handle == handle

        with db.create_session() as session:
            db.add_problems_from_contest('1656', session)
            session.commit()
            problems = session.query(models.Problem).all()
            assert len(problemsets) == 0
            users = db.get_users([models.UserType.PARTICIPANT], session)
            assert len(users) == 1
            assert users[0].handle == handle