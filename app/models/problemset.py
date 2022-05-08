import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base


class Problemset(Base):
    __tablename__ = 'problemsets'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=True)
    image = sa.Column(sa.String, nullable=False)
    problems = so.relationship(
        'Problem', secondary='problemlinks', back_populates='problemsets', uselist=True
    )
