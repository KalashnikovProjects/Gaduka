import gaduka_engine

from flask import jsonify
from flask_restful import Resource, abort, reqparse, Api
from ..data import db_session
from ..data.users import User


# parser = reqparse.RequestParser()
# parser.add_argument('name', required=True)
# parser.add_argument('about', required=True)
# parser.add_argument('email', required=True)
# parser.add_argument('hashed_password', required=True)
# parser.add_argument('created_date', required=True)


only = ('code', 'input_imgs')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")
    return session, user


class UsersResource(Resource):
    def get(self, user_id):
        _, user = abort_if_user_not_found(user_id)
        return jsonify(
            {"user": user.to_dict(only=only)}
        )

    def delete(self, user_id):
        session, user = abort_if_user_not_found(user_id)
        session.delete(user)
        session.commit()
        return jsonify({"success": "OK"})

    def put(self, user_id):
        ...


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify(
            {"user": [el.to_dict(only=only)
                      for el in user]}
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        kwa = {}
        for i in only:
            kwa[i] = args[i]
        user = User(**kwa)
        user.set_password(kwa["hashed_password"])
        session.add(user)
        session.commit()
        return jsonify({"success": "OK"})
