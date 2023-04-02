from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

@dataclass
class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    auth_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    projects = orm.relationship("Projects", back_populates='user')

    def __repr__(self):
        return f"{self.username}"

