from dataclasses import dataclass

import config
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, TINYTEXT, MEDIUMINT

from .db_session import SqlAlchemyBase


@dataclass
class Projects(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(MEDIUMINT, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(TINYTEXT, nullable=True, default="Новый проект")
    code = sqlalchemy.Column(MEDIUMTEXT, nullable=True, default="")
    img = sqlalchemy.Column(MEDIUMTEXT, nullable=True, default=config.DEFAULT_IMG)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

