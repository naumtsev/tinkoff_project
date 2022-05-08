import enum

import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base


class Rank(enum.Enum):
    NEWBIE = 1
    PUPIL = 2
    SPECIALIST = 3
    EXPERT = 4
    CANDIDATE_MASTER = 5
    MASTER = 6
    INTERNATIONAL_MASTER = 7
    GRANDMASTER = 8
    LEGENDARY_GRANDMASTER = 9

    @staticmethod
    def from_str(rank: str):
        if rank not in ranks:
            return None
        return ranks[rank]


ranks = {
    'newbie': Rank.NEWBIE,
    'pupil': Rank.PUPIL,
    'specialist': Rank.SPECIALIST,
    'expert': Rank.EXPERT,
    'candidate_master': Rank.CANDIDATE_MASTER,
    'master': Rank.MASTER,
    'international_master': Rank.INTERNATIONAL_MASTER,
    'grandmaster': Rank.GRANDMASTER,
    'legendary_grandmaster': Rank.LEGENDARY_GRANDMASTER,
}


class UserType(enum.Enum):
    PARTICIPANT = 0
    SPECTATOR = 1


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    handle = sa.Column(sa.String, unique=True, nullable=False, index=True)
    rank = sa.Column(sa.Enum(Rank), nullable=True)
    user_type = sa.Column(sa.Enum(UserType), nullable=True)
    submissions = so.relationship('Submission', back_populates='author', uselist=True)
