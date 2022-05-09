import contextlib
import typing

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import and_, or_

from app import codeforces_api, config
from app.models import Base, Problem, Problemset, Rank, User, UserType


class DB:
    def __init__(self) -> None:
        self._engine = sa.create_engine(config.DB_URL)
        self._session = so.sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    @contextlib.contextmanager
    def create_session(self, **kwargs: typing.Any) -> typing.Any:
        session = self._session(**kwargs)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_users(self, allowed_user_types: typing.List[UserType], session: typing.Any):
        criteries = [User.user_type == user_type for user_type in allowed_user_types]
        return session.query(User).filter(or_(*criteries)).all()

    def add_user(self, handle: str, user_type: UserType = UserType.PARTICIPANT):
        with self.create_session() as session:
            user = session.query(User).filter(User.handle == handle).one_or_none()
            if user is None:
                session.add(
                    User(handle=handle, user_type=user_type, rank=Rank.NOT_RANKED)
                )

    def add_problemset(
        self,
        title: str,
        description: str,
        problems: typing.List[typing.Tuple[str, str]],
        image_base64: str,
    ):
        valid_problems = []

        with self.create_session() as session:
            problem_set = Problemset(
                title=title, description=description, image=image_base64
            )
            session.add(problem_set)
            for (contest_id, problem_index) in problems:
                q = session.query(Problem).filter(
                    and_(
                        Problem.problem_index == problem_index,
                        Problem.contest_id == contest_id,
                    )
                )

                problem = q.one_or_none()

                if problem is None:
                    self.add_problems_from_contest(contest_id, session)

                problem = q.one_or_none()
                if problem is not None:
                    valid_problems.append((contest_id, problem_index))
                    problem_set.problems.append(problem)
        return valid_problems

    def add_problems_from_contest(self, contest_id, session):
        problems = codeforces_api.get_contest_problems(contest_id)
        for problem in problems:
            title = problem['name']
            contest_id = problem['contestId']
            problem_index = problem['index']
            rating = problem.get('rating', 0)

            problem = (
                session.query(Problem)
                .filter(
                    and_(
                        Problem.problem_index == problem_index,
                        Problem.contest_id == contest_id,
                    )
                )
                .one_or_none()
            )

            if problem is None:
                session.add(
                    Problem(
                        contest_id=contest_id,
                        problem_index=problem_index,
                        rating=rating,
                        title=title,
                    )
                )


db = DB()
