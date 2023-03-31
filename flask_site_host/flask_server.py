import base64
import json
from datetime import timedelta

import requests
from flask_restful import Api
from flask import Flask, render_template, request, session, make_response, redirect, jsonify, abort, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, login_manager
from flask_site_host.forms.code_page import SaveProjectForm
from flask_site_host.api_server import gaduka_api, database_api
from flask_site_host.data import db_session
from flask_site_host.data.projects import Projects
from flask_site_host.data.users import User
import requests
import hashlib
import hmac
import config
from flask_site_host.code_examples import EXAMPLES


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '/mops/delete/up/pack/super214jmi3rg4nsnfaqta/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    days=3650
)
login_manager = LoginManager()
login_manager.init_app(app)


class ToClass:
    def __init__(self, d: dict):
        self.d = d
        self.is_authenticated = True

    def get_value(self):
        return self.d

    def is_active(self):
        return True

    def get_id(self):
        return self.d["username"]

    def __getattr__(self, item: str):
        if item not in ("is_active", "get_id", "d", "get_value", "is_authenticated"):
            return self.d.get(item)
        else:
            return self.__dict__[item]

    def __repr__(self):
        return repr(self.d)

    def __call__(self, *args, **kwargs):
        return self.get_value()

@app.errorhandler(404)
def not_found(error):
    return render_template("error_page.html", error="Такой страницы не существует.")


@app.errorhandler(400)
def bad_request(_):
    return render_template("error_page.html", error="Ошибка оформления запроса.")


@login_manager.user_loader
def load_user(user_id):
    resp = requests.get(f"{config.database_server}/api/v1/users/{user_id}").json()
    user = ToClass(resp["user"])
    return user


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Язык программирования Гадюка", examples=EXAMPLES)

@app.route('/users/<username>')
def user_page(username):

    resp = requests.get(f"{config.database_server}/api/v1/users/{username}").json()
    if "user" not in resp:
        return render_template("error_page.html", error='Такого профиля не существует', title='Такого профиля не существует')
    projects = [ToClass(i) for i in resp['user']['projects']]
    return render_template('user_page.html', user_page_name=username, title=f"Профиль {username}", projects=projects)


def check_user(user):
    # Проверка правильности данных регистрации

    d = user.copy()
    del d['hash']
    d_list = []
    for key in sorted(d.keys()):
        if d[key] is not None:
            d_list.append(key + '=' + str(d[key]))
    data_string = bytes('\n'.join(d_list), 'utf-8')

    secret_key = hashlib.sha256(config.BOT_TOKEN.encode('utf-8')).digest()
    return hmac.new(secret_key, data_string, hashlib.sha256).hexdigest() == user['hash']


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", title=f"Вход в аккаунт")
    user_data = request.json
    if not check_user(user_data):
        return bad_request()

    resp = requests.get(f"{config.database_server}/api/v1/users/{user_data['id']}").json()
    if "user" not in resp:
        requests.post(f"{config.database_server}/api/v1/users/",
            json={
                "id": user_data['id'],
                "username": user_data['username'],
                "photo_url": user_data['photo_url'],
                "auth_date": user_data['auth_date'],
                'token': config.REST_API_TOKENS[1]
            })
        resp = requests.get(f"{config.database_server}/api/v1/users/{user_data['id']}").json()
    user = ToClass(resp["user"])
    login_user(user, remember=True)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/login_error')
def login_error_page():
    return render_template('error_page.html', title="Ошибка при входе в аккаунт", error='Произошла ошибка при регистрации')


@login_required
@app.route('/run_code', methods=['GET', "POST"])
def run_code():
    form = SaveProjectForm()
    return render_template('code_page.html', title='Запуск кода', form=form)


@app.route('/create_project', methods=['GET'])
@login_required
def create_project():
    project = requests.post(f"{config.database_server}/api/v1/projects",
                    json={
                      "name": "Новый проект",
                      "code": "",
                      "user_id": current_user.id,
                      'token': config.REST_API_TOKENS[1]
                    }).json()
    pr_id = project["project_id"]
    return redirect(f"/projects/{pr_id}")

@app.route('/projects/<int:project_id>', methods=['GET', "POST"])
def projects_page(project_id):
    form = SaveProjectForm()
    if form.validate_on_submit():
        if form.submit.data:
            if form.images.data:
                form.images.data.stream.seek(0)
                a = form.images.data.read()
                img = str(base64.b64encode(a))[2:-1]
                print(img)
                requests.put(f"{config.database_server}/api/v1/projects/{project_id}",
                             json={
                                 "name": form.name.data,
                                 "code": form.code.data,
                                 "img": img,
                                 'token': config.REST_API_TOKENS[1]
                             })
            else:
                requests.put(f"{config.database_server}/api/v1/projects/{project_id}",
                             json={
                                 "name": form.name.data,
                                 "code": form.code.data,
                                 'token': config.REST_API_TOKENS[1]
                             })
                project = requests.get(f"{config.database_server}/api/v1/projects/{project_id}").json()
                print(1, project)
            return '', 204

        else:
            requests.delete(f"{config.database_server}/api/v1/projects/{project_id}",
                         json={'token': config.REST_API_TOKENS[1]})
            return redirect(f"/users/{current_user.username}")

    project = requests.get(f"{config.database_server}/api/v1/projects/{project_id}").json()
    if "project" not in project:
        return render_template("error_page.html", error="Такого проекта не существует")

    print(project)
    project = project['project']
    form.name.data = project["name"]
    form.code.data = project['code']
    author = project["user"]['username']
    if current_user.is_authenticated and author == current_user.username:
        template = 'my_project_page.html'
    else:
        template = 'project_page.html'

    return render_template(template, title=f'Гадюка проект {project["name"]}', form=form, author=author)


def check_image(img_url):
    # Не работает
    # Автомодерация изображений, перед тем, как поставить их на обложку проекта
    url = 'https://app.nanonets.com/api/v2/OCR/Model/353cea12-4dcc-47ee-b139-dd345157b17d/LabelFile/'

    headers = {'accept': 'application/x-www-form-urlencoded'}

    data = {'file': img_url}

    response = requests.request('POST', url, headers=headers,
                                auth=requests.auth.HTTPBasicAuth(config.NANONETS_API_TOKEN, ''),
                                files=data).json()
    res = response['result']
    return not res['prediction'][0]["probability"] > 0.3


def main():

    if __name__ == "__main__":
        db_session.global_init("db/main_gaduka.db")
    else:
        db_session.global_init("flask_site_host/db/main_gaduka.db")
    api.add_resource(database_api.UsersListResource, "/api/v1/users")
    api.add_resource(database_api.UsersResource, "/api/v1/users/<user_id>")
    api.add_resource(database_api.ProjectsListResource, "/api/v1/projects")
    api.add_resource(database_api.ProjectsResource, "/api/v1/projects/<int:project_id>")
    if __name__ == "__main__":
        app.run(port=config.PORT, host='127.0.0.1')
    else:
        return app


if __name__ == '__main__':
    main()
