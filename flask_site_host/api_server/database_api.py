import config
import gaduka_engine

from flask import jsonify
from flask_restful import Resource, abort, reqparse, Api
from ..data import db_session
from ..data.users import User
from ..data.projects import Projects


create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('token', required=True)
create_user_parser.add_argument('id', required=True)
create_user_parser.add_argument('username', required=True)
create_user_parser.add_argument('photo_url')
create_user_parser.add_argument('auth_date')

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('token', required=True)

create_project_parser = reqparse.RequestParser()
create_project_parser.add_argument('token', required=True)
create_project_parser.add_argument('name')
create_project_parser.add_argument('code')
create_project_parser.add_argument('img')
create_project_parser.add_argument('user_id', required=True)

user_only = ('username', 'photo_url', 'auth_date')
project_only = ('name', 'code', 'img', 'user.id', 'user.name')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()

    user = session.get(User, user_id)
    if not user:
        abort(404, message=f"Пользователь {user_id} не найден")
    return session, user


def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.get(Projects, project_id)
    if not project:
        abort(404, message=f"Проект {project_id} не найден")
    return session, project


def abort_id_already_taken(user_id):
    session = db_session.create_session()
    user = session.get(User, user_id)
    if user:
        abort(404, message=f"Пользователь с id {user_id} уже существует")
    session.close()


def abort_if_token_error(token):
    if token not in config.REST_API_TOKENS:
        abort(401, message=f"Несуществующий токен")


class UsersResource(Resource):
    def get(self, user_id):
        _, user = abort_if_user_not_found(user_id)
        return jsonify({"user": user})


    def delete(self, user_id):
        args = delete_parser.parse_args()
        abort_if_token_error(args['token'])
        session, user = abort_if_user_not_found(user_id)
        session.delete(user)
        session.commit()
        return jsonify({"success": "OK"})

    def put(self, user_id):
        # Пока что не нужен
        ...


class UsersListResource(Resource):
    def post(self, user_id):
        # id пользователя в базе данных совпадает с id пользователя telegram
        args = create_user_parser.parse_args()
        abort_if_token_error(args['token'])
        abort_id_already_taken(user_id)
        session = db_session.create_session()
        kwa = {}
        for i in user_only:
            kwa[i] = args[i]
        user = User(**kwa)
        session.add(user)
        session.commit()
        return jsonify({"success": "OK"})


class ProjectsResource(Resource):
    def get(self, project_id):
        _, project = abort_if_project_not_found(project_id)
        return jsonify({"project": project})

    def delete(self, project_id):
        args = delete_parser.parse_args()
        abort_if_token_error(args['token'])
        session, project = abort_if_project_not_found(project_id)
        session.delete(project)
        session.commit()
        return jsonify({"success": "OK"})

    def put(self, project_id):
        ...


class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Projects).all()
        return jsonify({'projects': projects})

    def post(self):
        args = create_project_parser.parse_args()
        abort_if_token_error(args['token'])
        session = db_session.create_session()
        kwa = {}
        for i in project_only:
            kwa[i] = args[i]
        user = Projects(**kwa)
        session.add(user)
        session.commit()
        return jsonify({"success": "OK"})
