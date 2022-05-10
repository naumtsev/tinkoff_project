import enum
import typing

import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base


class Rank(enum.Enum):
    NOT_RANKED = 0
    NEWBIE = 1
    PUPIL = 2
    SPECIALIST = 3
    EXPERT = 4
    CANDIDATE_MASTER = 5
    MASTER = 6
    INTERNATIONAL_MASTER = 7
    GRANDMASTER = 8
    INTERNATIONAL_GRANDMASTER = 9
    LEGENDARY_GRANDMASTER = 10

    @staticmethod
    def from_str(rank: str) -> typing.Any:
        if rank not in _ranks:
            return Rank.NOT_RANKED
        return _ranks[rank]


def get_rank_color(rank: Rank) -> str:
    return _ranks_color[rank]


_ranks = {
    'newbie': Rank.NEWBIE,
    'pupil': Rank.PUPIL,
    'specialist': Rank.SPECIALIST,
    'expert': Rank.EXPERT,
    'candidate master': Rank.CANDIDATE_MASTER,
    'master': Rank.MASTER,
    'international master': Rank.INTERNATIONAL_MASTER,
    'grandmaster': Rank.GRANDMASTER,
    'international grandmaster': Rank.INTERNATIONAL_GRANDMASTER,
    'legendary grandmaster': Rank.LEGENDARY_GRANDMASTER,
}

_ranks_color = {
    Rank.NOT_RANKED: '#000000',
    Rank.NEWBIE: '#808080',
    Rank.PUPIL: '#008000',
    Rank.SPECIALIST: '#03a89e',
    Rank.EXPERT: '#0000ff',
    Rank.CANDIDATE_MASTER: '#a0a',
    Rank.MASTER: '#ff8c00',
    Rank.INTERNATIONAL_MASTER: '#ff8c00',
    Rank.GRANDMASTER: '#ff0000',
    Rank.INTERNATIONAL_GRANDMASTER: '#ff0000',
    Rank.LEGENDARY_GRANDMASTER: '#CC0605',
}


class UserType(enum.Enum):
    PARTICIPANT = 0
    SPECTATOR = 1


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    handle = sa.Column(sa.String, unique=True, nullable=False, index=True)
    rank = sa.Column(sa.Enum(Rank), nullable=False)
    user_type = sa.Column(sa.Enum(UserType), nullable=True)
    submissions = so.relationship('Submission', back_populates='author', uselist=True)
