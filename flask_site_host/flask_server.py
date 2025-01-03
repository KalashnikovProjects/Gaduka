import base64
import json
import secrets
import time
from datetime import timedelta
import logging
import hashlib
import hmac

import retry
from flask_restful import Api
from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import select, update, delete

from .forms.code_page import SaveProjectForm
from .api_server import database_api
from .data import db_session
from .data.projects import Projects
from .data.users import User
from .code_examples import EXAMPLES
from . import config

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3650)
login_manager = LoginManager()
login_manager.init_app(app)
api.add_resource(database_api.UsersListResource, "/api/v1/users")
api.add_resource(database_api.UsersResource, "/api/v1/users/<int:user_id>")
api.add_resource(database_api.ProjectsListResource, "/api/v1/projects")
api.add_resource(database_api.ProjectsResource, "/api/v1/projects/<int:project_id>")


@app.errorhandler(500)
def server_error(error):
    logging.error(error)
    return render_template("error_page.html", error="Произошла непредвиденная ошибка на стороне сервера.")


@app.errorhandler(404)
def not_found(_):
    return render_template("error_page.html", error="Такой страницы не существует.")


@app.errorhandler(400)
def bad_request(_):
    return render_template("error_page.html", error="Ошибка оформления запроса.")


@login_manager.user_loader
@retry.retry(tries=3, delay=2)
def load_user(user_id):
    with db_session.create_session() as db_sess:
        stmt = select(User).where(User.id == user_id)
        user = db_sess.scalar(stmt)
        return user


@app.route('/logout')
@retry.retry(tries=3, delay=2)
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
@retry.retry(tries=3, delay=2)
def index():
    return render_template('index.html', title="Язык программирования Гадюка", examples=EXAMPLES)


@app.route('/users/<username>')
@retry.retry(tries=3, delay=2)
def user_page(username):
    with db_session.create_session() as db_sess:
        stmt = select(User).where(User.username == username)
        user = db_sess.scalar(stmt)
        if not user:
            return render_template("error_page.html", error='Такого профиля не существует', title='Такого профиля не существует')

        stmt = select(Projects).where(Projects.user_id == user.id)
        projects = db_sess.scalars(stmt).all()

        return render_template('user_page.html', user_page_name=username, title=f"Профиль {username}", projects=projects)


# Проверяет валидность логина через телеграм
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


@app.route('/login', methods=["GET"])
@retry.retry(tries=3, delay=2)
def login_page():
    return render_template("login.html", title=f"Вход в аккаунт", telegram_bot_name=config.TELEGRAM_BOT_NAME)


@app.route('/login', methods=["POST"])
@retry.retry(tries=3, delay=2)
def login_post():
    user_data = request.json
    if not check_user(user_data):
        return bad_request()

    with db_session.create_session() as db_sess:
        stmt = select(User).where(User.id == user_data['id'])
        user = db_sess.scalar(stmt)
        if not user:
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                photo_url=user_data.get('photo_url', "https://communitylivinghamilton.com/wp-content/uploads/headshot-silhouette.jpg"),
                auth_date=user_data['auth_date'],
            )
            db_sess.add(user)
            db_sess.commit()
        login_user(user, remember=True)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/login_error')
@retry.retry(tries=3, delay=2)
def login_error_page():
    return render_template('error_page.html', title="Ошибка при входе в аккаунт", error='Произошла ошибка при регистрации')


@app.route('/run_code', methods=['GET', "POST"])
@retry.retry(tries=3, delay=2)
def run_code():
    form = SaveProjectForm()
    return render_template('code_page.html', title='Запуск кода', code_run_api_url=config.CODE_RUN_API, form=form)


@app.route('/create_project', methods=['GET'])
@login_required
@retry.retry(tries=3, delay=2)
def create_project():
    with db_session.create_session() as db_sess:
        project = Projects(
            name="Новый проект",
            code='',
            user_id=current_user.id)
        db_sess.add(project)
        db_sess.commit()
        project_id = project.id
        return redirect(f"/projects/{project_id}")


@app.route('/projects/<int:project_id>', methods=['GET', "POST"])
@retry.retry(tries=3, delay=2)
def projects_page(project_id):
    form = SaveProjectForm()
    with db_session.create_session() as db_sess:
        if form.validate_on_submit():
            stmt = select(Projects).where(Projects.id == project_id)
            project = db_sess.scalar(stmt)
            if form.submit.data:
                stmt = update(Projects).where(Projects.id == project.id).values(name=form.name.data, code=form.code.data)
                if form.images.data:
                    form.images.data.stream.seek(0)
                    a = form.images.data.read()
                    img = str(base64.b64encode(a)).strip("b'")
                    # if check_image(a):
                    stmt = stmt.values(img=img)
                db_sess.execute(stmt)
                db_sess.commit()
                return '', 204
            else:
                stmt = delete(Projects).where(Projects.id == project.id)
                db_sess.execute(stmt)
                db_sess.commit()
                return redirect(f"/users/{current_user.username}")

        stmt = select(Projects).where(Projects.id == project_id)
        project = db_sess.scalar(stmt)
        if not project:
            return render_template("error_page.html", error="Такого проекта не существует")

        form.name.data = project.name
        form.code.data = project.code
        author = project.user.username
        if current_user.is_authenticated and author == current_user.username:
            template = 'my_project_page.html'
        else:
            template = 'project_page.html'

        return render_template(template, title=f'Гадюка проект {project.name}', code_run_api_url=config.CODE_RUN_API, form=form, author=author)


def main():
    attempt = 1
    while True:
        try:
            db_session.global_init()
        except Exception as e:
            logging.warning(f"Ошибка при инициализации подключения к базе данных {e}, попытка {attempt}")
            time.sleep(20)
            attempt += 1
        else:
            logging.info("База данных подключена")
            break
    return app.run(port=config.FLASK_SERVER_PORT, host='0.0.0.0')


if __name__ == '__main__':
    main()
