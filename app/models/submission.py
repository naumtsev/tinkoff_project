import enum

import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base


class Verdict(enum.Enum):
    OK = 1
    FAILED = 2


class Submission(Base):
    __tablename__ = 'submissions'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    author_handle = sa.Column(sa.String, sa.ForeignKey('users.handle'))
    author = so.relationship('User', back_populates='submissions', uselist=False)

    verdict = sa.Column(sa.Enum(Verdict))
    creation_time = sa.Column(sa.Integer, nullable=False)

    contest_id = sa.Column(
        sa.String, sa.ForeignKey('problems.contest_id'), nullable=True
    )
    problem_index = sa.Column(
        sa.String, sa.ForeignKey('problems.problem_index'), nullable=False
    )
