import typing
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler

from app import codeforces_api, config, models
from app.db import db


def update_users_info() -> None:
    with db.create_session() as session:
        users = session.query(models.User).all()
        handles = []
        d_users: typing.Dict[str, models.User] = {}

        for user in users:
            handles.append(str(user.handle))
            d_users[str(user.handle)] = user

        for user_info in codeforces_api.get_users_info(handles):
            handle = user_info['handle']
            rank = user_info.get('rank', '')
            d_users[handle].rank = models.Rank.from_str(rank)


def _update_user_submissions(handle: str) -> None:
    with db.create_session() as session:
        user = (
            session.query(models.User)
            .filter(models.User.handle == handle)
            .one_or_none()
        )
        if user is None:
            return

        current_submissions = codeforces_api.get_user_submissions(handle)
        submissions: typing.List[models.Submission] = (
            session.query(models.Submission)
            .filter(models.Submission.author_handle == handle)
            .all()
        )

        used_submissions = {}
        for sub in submissions:
            used_submissions[sub.cf_id] = True

        for sub in current_submissions:
            if sub['id'] not in used_submissions:
                verdict = models.Verdict.FAILED
                if sub['verdict'] == 'OK':
                    verdict = models.Verdict.OK

                user.submissions.append(
                    models.Submission(
                        cf_id=sub['id'],
                        author_handle=handle,
                        verdict=verdict,
                        creation_time=sub['creationTimeSeconds'],
                        contest_id=sub['problem']['contestId'],
                        problem_index=sub['problem']['index'],
                    )
                )


def update_users_submissions() -> None:
    executors = ThreadPoolExecutor(max_workers=3)
    handles = []
    with db.create_session() as session:
        users = (
            session.query(models.User)
            .filter(models.User.user_type == models.UserType.PARTICIPANT)
            .all()
        )
        for user in users:
            handles.append(user.handle)

    for handle in handles:
        executors.submit(_update_user_submissions, handle)


workers_scheduler: BackgroundScheduler = BackgroundScheduler()
workers_scheduler.add_job(
    update_users_submissions, 'interval', seconds=config.USERS_INFO_UPDATE_TIME
)
workers_scheduler.add_job(
    update_users_info, 'interval', seconds=config.USERS_SUBMISSIONS_UPDATE_TIME
)
