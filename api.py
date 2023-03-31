import os
from datetime import timedelta
from flask import Flask
from flask_restful import Api

from api_server import database_api
from data import db_session

app = Flask(__name__)

from flask_cors import  CORS
rs = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    days=3650
)

@app.route("/")
def no_sleep():
    return "Это закрытое api"


db_session.global_init(".data/main_gaduka.db")
api.add_resource(database_api.UsersListResource, "/api/v1/users")
api.add_resource(database_api.UsersResource, "/api/v1/users/<user_id>")
api.add_resource(database_api.ProjectsListResource, "/api/v1/projects")
api.add_resource(database_api.ProjectsResource, "/api/v1/projects/<int:project_id>")