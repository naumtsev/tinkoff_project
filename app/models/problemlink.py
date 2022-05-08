import sqlalchemy as sa

from .base import Base


class Problemlink(Base):
    __tablename__ = 'problemlinks'
    id = sa.Column(sa.Integer, primary_key=True)
    problem_id = sa.Column(sa.Integer, sa.ForeignKey('problems.id'))
    problemset_id = sa.Column(sa.Integer, sa.ForeignKey('problemsets.id'))
    problem_position = sa.Column(sa.Integer, default=0)
