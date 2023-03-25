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

import hashlib
import hmac
import config



app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '/mops/delete/up/pack/super214jmi3rg4nsnfaqta/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    days=3650
)
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template("error_page.html", error="Такого проекта не существует.")


@app.errorhandler(400)
def bad_request(_):
    return render_template("error_page.html", error="Ошибка оформления запроса.")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    a = db_sess.get(User, user_id)
    db_sess.close()
    return a


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Язык программирования Гадюка")

@app.route('/users/<username>')
def user_page(username):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.username == username).first()
    projects = db_sess.query(Projects).filter(User.username == username).all()
    if not user:
        return render_template("error_page.html", error='Такого профиля не существует', title='Такого профиля не существует')

    return render_template('user_page.html', user_page_name=username, title=f"Профиль {username}", projects=projects)


def check_user(user):
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

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_data['id']).first()
    if not user:
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            photo_url=user_data['photo_url'],
            auth_date=user_data['auth_date'],
        )
        db_sess.add(user)
        db_sess.commit()
    login_user(user, remember=True)
    db_sess.close()
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
    db_sess = db_session.create_session()
    project = Projects(
        name="Новый проект",
        code='',
        user_id=current_user.id)
    db_sess.add(project)
    db_sess.commit()
    return redirect(f"/projects/{project.id}")

@app.route('/projects/<int:project_id>', methods=['GET', "POST"])
def projects_page(project_id):
    form = SaveProjectForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        project = db_sess.get(Projects, project_id)
        if form.submit.data:
            project.name = form.name.data
            project.code = form.code.data
            if form.images.data:
                form.images.data.stream.seek(0)
                a = form.images.data.read()
                img = str(base64.b64encode(a)).strip("b'")
                # if check_image(a):
                project.img = img
            db_sess.commit()
            return '', 204

        else:
            db_sess.delete(project)
            db_sess.commit()
            return redirect(f"/users/{current_user.username}")

    db_sess = db_session.create_session()

    project = db_sess.get(Projects, project_id)
    if not project:
        abort(404)

    db_sess.commit()
    form.name.data = project.name
    form.code.data = project.code
    author = project.user.username
    db_sess.close()
    if current_user.is_authenticated and author == current_user.username:
        template = 'my_project_page.html'
    else:
        template = 'project_page.html'

    return render_template(template, title=f'Гадюка проект {project.name}', form=form, author=author)


def check_image(img_url):
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
    api.add_resource(gaduka_api.GadukaRunCodeApi, "/api/v1/engine")
    api.add_resource(database_api.UsersListResource, "/api/v1/users")
    api.add_resource(database_api.UsersResource, "/api/v1/users/<int:user_id>")
    api.add_resource(database_api.ProjectsListResource, "/api/v1/projects")
    api.add_resource(database_api.ProjectsResource, "/api/v1/projects/<int:project_id>")

    app.run(port=config.PORT, host='127.0.0.1')


if __name__ == '__main__':
    main()
