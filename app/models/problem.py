import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base


class Problem(Base):
    __tablename__ = 'problems'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)

    contest_id = sa.Column(sa.String, nullable=False, index=True)
    problem_index = sa.Column(sa.String, nullable=False)

    rating = sa.Column(sa.Integer, default=0)
    problemsets = so.relationship(
        'Problemset', secondary='problemlinks', back_populates='problems'
    )

    sa.CheckConstraint(contest_id, problem_index)
