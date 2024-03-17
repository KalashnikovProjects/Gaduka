import base64
import json
import logging
from datetime import timedelta

from flask_restful import Api
from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_site_host.forms.code_page import SaveProjectForm
from flask_site_host.api_server import gaduka_api, database_api
from flask_site_host.data import db_session
from flask_site_host.data.projects import Projects
from flask_site_host.data.users import User
from sqlalchemy import update, select, delete

import time
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
api.add_resource(database_api.UsersListResource, "/api/v1/users")
api.add_resource(database_api.UsersResource, "/api/v1/users/<int:user_id>")
api.add_resource(database_api.ProjectsListResource, "/api/v1/projects")
api.add_resource(database_api.ProjectsResource, "/api/v1/projects/<int:project_id>")
api.add_resource(gaduka_api.GadukaRunCodeApi, "/api/v1/engine")

@app.errorhandler(500)
def server_error(error):
    logging.error(error)
    return render_template("error_page.html", error="Произошла непредвиденная ошибка на стороне сервера.")


@app.errorhandler(404)
def not_found(error):
    return render_template("error_page.html", error="Такой страницы не существует.")


@app.errorhandler(400)
def bad_request(_):
    return render_template("error_page.html", error="Ошибка оформления запроса.")


@login_manager.user_loader
def load_user(user_id):
    for i in range(3):
        try:
            with db_session.create_session() as db_sess:
                stmt = select(User).where(User.id == user_id)
                user = db_sess.scalar(stmt)
                return user
        except Exception as e:
            logging.warning(f"Ошибка при запросе в бд {e}, попытка {i + 1}/3")
            time.sleep(3)
    logging.error(f"База данных не отвечает")
    raise


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


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", title=f"Вход в аккаунт")
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

        return render_template(template, title=f'Гадюка проект {project.name}', form=form, author=author)



def main():
    if __name__ == "__main__":
        db_session.global_init("db/main_gaduka.db")
    else:
        db_session.global_init("flask_site_host/db/main_gaduka.db")
    logging.info("База данных подключена")
    app.run(port=config.PORT, host='0.0.0.0')


if __name__ == '__main__':
    main()
