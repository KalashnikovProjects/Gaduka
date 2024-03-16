from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMTEXT, TINYTEXT


@dataclass
class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(BIGINT,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(TINYTEXT, nullable=True)
    photo_url = sqlalchemy.Column(MEDIUMTEXT, nullable=True)
    auth_date = sqlalchemy.Column(TINYTEXT, nullable=True)

    projects = orm.relationship("Projects", backref='user')

    def __repr__(self):
        return f"{self.username}"
