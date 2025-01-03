from dataclasses import dataclass

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.postgresql import TEXT, INTEGER, BIGINT

from .. import config
from .db_session import SqlAlchemyBase


@dataclass
class Projects(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(INTEGER, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(TEXT, nullable=True, default="Новый проект")
    code = sqlalchemy.Column(TEXT, nullable=True, default="")
    img = sqlalchemy.Column(TEXT, nullable=True, default=config.DEFAULT_IMG)

    user_id = sqlalchemy.Column(BIGINT, sqlalchemy.ForeignKey("users.id"))
