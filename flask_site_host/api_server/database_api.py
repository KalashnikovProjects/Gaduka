import retry
from sqlalchemy import select

import config
from flask import jsonify
from flask_restful import Resource, abort, reqparse
from flask_site_host.data import db_session
from flask_site_host.data.users import User
from flask_site_host.data.projects import Projects


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
create_project_parser.add_argument('name', required=True)
create_project_parser.add_argument('code')
create_project_parser.add_argument('img')
create_project_parser.add_argument('user_id', required=True)

edit_project_parser = reqparse.RequestParser()
edit_project_parser.add_argument('token', required=True)
edit_project_parser.add_argument('name')
edit_project_parser.add_argument('code')
edit_project_parser.add_argument('img')

user_only = ("id", 'username', 'photo_url', 'auth_date')
project_only = ("id", 'name', 'code', 'img', 'user.id', 'user.username')
project_edit_only = ('name', 'code', 'img')
project_create_only = ('name', 'code', 'img', "user_id")


def abort_if_user_not_found(user_id: str):
    with db_session.create_session() as session:
        if user_id.isdigit():
            user = session.get(User, user_id)
        else:
            user = (session.execute(
                select(User).where(User.username == user_id)
            )).scalar_one_or_none()
        if not user:
            abort(404, message=f"Пользователь {user_id} не найден")
    return user


def abort_if_project_not_found(project_id):
    with db_session.create_session() as session:
        project = session.get(Projects, project_id)
        if not project:
            abort(404, message=f"Проект {project_id} не найден")
    return project


def abort_id_already_taken(user_id):
    with db_session.create_session() as session:
        user = session.get(User, user_id)
        if user:
            abort(404, message=f"Пользователь с id {user_id} уже существует")


def abort_if_token_error(token):
    if token not in config.REST_API_TOKENS:
        abort(401, message=f"Несуществующий токен")


class UsersResource(Resource):
    @retry.retry(tries=3, delay=2)
    def get(self, user_id):
        user = abort_if_user_not_found(str(user_id))
        a = user.to_dict(only=user_only)
        a['projects'] = []
        for i in user.projects:
            a['projects'].append(i.to_dict(only=("id", 'name', 'img')))
        return jsonify({"user": a})

    @retry.retry(tries=3, delay=2)
    def delete(self, user_id):
        args = delete_parser.parse_args()
        abort_if_token_error(args['token'])
        with db_session.create_session() as session:
            user = abort_if_user_not_found(user_id)
            session.delete(user)
            session.commit()
        return jsonify({"success": "OK"})


class UsersListResource(Resource):
    @retry.retry(tries=3, delay=2)
    def post(self):
        args = create_user_parser.parse_args()
        abort_if_token_error(args['token'])
        abort_id_already_taken(args["id"])
        with db_session.create_session() as session:
            kwa = {}
            for i in user_only:
                kwa[i] = args[i]
            user = User(**kwa)
            session.add(user)
            session.commit()
        return jsonify({"success": "OK"})


class ProjectsResource(Resource):
    @retry.retry(tries=3, delay=2)
    def get(self, project_id):
        project = abort_if_project_not_found(project_id)
        return jsonify({"project": project.to_dict(only=project_only)})

    @retry.retry(tries=3, delay=2)
    def delete(self, project_id):
        args = delete_parser.parse_args()
        abort_if_token_error(args['token'])
        with db_session.create_session() as session:
            project = abort_if_project_not_found(project_id)
            session.delete(project)
            session.commit()
        return jsonify({"success": "OK"})

    @retry.retry(tries=3, delay=2)
    def put(self, project_id):
        args = edit_project_parser.parse_args()
        abort_if_token_error(args['token'])
        with db_session.create_session() as session:
            project = abort_if_project_not_found(project_id)
            for i in set(args.keys()) & set(project_edit_only):
                setattr(project, i, args[i])
            session.commit()
        return jsonify({"success": "OK"})


class ProjectsListResource(Resource):
    @retry.retry(tries=3, delay=2)
    def get(self):
        with db_session.create_session() as session:
            projects = session.execute(select(Projects)).scalars().all()
            return jsonify({'projects': [i.to_dict(only=project_only) for i in projects]})

    @retry.retry(tries=3, delay=2)
    def post(self):
        args = create_project_parser.parse_args()
        abort_if_token_error(args['token'])
        with db_session.create_session() as session:
            kwa = {}
            for i in project_create_only:
                kwa[i] = args[i]
            project = Projects(**kwa)
            session.add(project)
            session.commit()
            user = session.get(User, args['user_id'])
            pr_id = user.projects[-1].id
        return jsonify({"success": "OK", "project_id": pr_id})
