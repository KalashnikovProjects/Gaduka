from dataclasses import dataclass

import config
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


@dataclass
class Projects(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="Новый проект")
    code = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="")
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=config.DEFAULT_IMG)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
