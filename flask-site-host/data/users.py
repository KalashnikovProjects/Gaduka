import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    auth_date = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hash = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    quota = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    projects = orm.relationship("Projects", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"{self.username}"

