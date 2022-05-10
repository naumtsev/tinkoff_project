import json

from app import config, models, workers
from app.app import app
from app.db import db
import io
from app import utils

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

        test_client.post('/add-user', data={'handle': handle}, content_type="application/x-www-form-urlencoded")
        with db.create_session() as session:
            user = (
                session.query(models.User)
                .filter(models.User.handle == handle)
                .one_or_none()
            )
            assert user is not None
            assert user.handle == handle

        workers.update_users_info()
        test_client.get(f'/update_users_info')

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

        test_client.get(f'/update_users_submissions')
        requests_mock.get(url_user_submissions, json=data)

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
                'image': (io.BytesIO(b""), 'img.jpg'),
                'problems': '1656A 1656B 1656C',
            },
            content_type='multipart/form-data'
        )

        problemset_id = None
        with db.create_session() as session:
            problemsets = session.query(models.Problemset).all()
            assert len(problemsets) == 1
            problemset = problemsets[0]
            assert problemset.title == 'test #1'
            assert problemset.description == 'test description'
            problemset_id = problemset.id
            assert len(problemset.problems) == 3

        test_client.post(
            f'/problemset/{problemset_id}',
            data={
                'title': 'test #2',
                'description': 'test description #2',
                'problems': '1656A 1656C',
            },
            content_type='multipart/form-data'
        )

        with db.create_session() as session:
            users = db.get_users([models.UserType.PARTICIPANT], session)
            assert len(users) == 1
            assert users[0].handle == handle
            problemset = session.query(models.Problemset).first()
            assert problemset.title == 'test #2'
            assert problemset.description == 'test description #2'
            assert len(problemset.problems) == 2

        # rendered html

        test_client.get(f'/problemset/{problemset_id}/standings')
        test_client.get(f'/problemset/{problemset_id}/standings')
        test_client.get(f'/problemset')
        test_client.get(f'/problemset/{problemset_id}')
        test_client.get(f'/users')


        test_client.post(f'/change_user_type/{handle}', data={'user_type': models.UserType.SPECTATOR.value})

    with db.create_session() as session:
        user = db.get_user_by_handle(handle, session)
        assert user.user_type == models.UserType.SPECTATOR


def test_parse_problems():
    problems = utils.parse_problems('11A 12B 13C 12B 13C 144E 144')
    assert problems == [('11', 'A'), ('12', 'B'), ('13', 'C'), ('144', 'E')]
