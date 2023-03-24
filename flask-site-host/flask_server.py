import json
from datetime import timedelta

import requests
from flask_restful import Api
from flask import Flask, render_template, request, session, make_response, redirect, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, login_manager
from forms.run_code import CodeRunForm
import hashlib
import hmac
import config
import random
from api_server import gaduka_api
from data import db_session
from data.projects import Projects
from data.users import User


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
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    a = db_sess.query(User).get(user_id)
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
    logged = True
    my_username = 'Kalashnik'

    return render_template('index.html', my_username=my_username, logged=logged, title="Язык программирования Гадюка")


@app.route('/users/<username>')
def user_page(username):
    logged = True
    my_username = 'Kalashnik'

    exist_user = True
    a = ("/static/img/gaduka-icon.png",
         "/static/img/tg-icon.png",
         "/static/img/result_img_2.png",
         "/static/img/result_img_1.png")
    b = ("Проект", "Эксперимент", "eagnaiegu;g")
    projects = enumerate(((f"{random.choice(b)} {j}", random.choice(a)) for j in range(30)))
    if not exist_user:
        return render_template("user_error_page.html", my_username=my_username, logged=logged)

    return render_template('user_page.html', my_username=my_username, logged=logged,
                           user_page_name=username, projects=projects, title=f"Профиль {my_username}")


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
    elif request.method == "POST":
        user_data = request.json
        if check_user(user_data):
            session['formdata'] = request.json
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return bad_request()


@app.route('/login_error')
def login_error_page():
    return render_template('login_error_page.html', title="Ошибка при входе в аккаунт")


@app.route('/run_code', methods=['GET', "POST"])
def run_code():
    form = CodeRunForm()
    print(form.images.data)

    if form.validate_on_submit():
        code, img = form.code, form.images
        # pics = request.files.getlist(form.images.name)
        # print(pics)
        # if pics:
        #     for picture_upload in pics:
        #         picture_contents = picture_upload.stream.read()
        #         print(type(picture_contents))

        a = gaduka_api.run_with_json_images_input(code.data, img.data)

        return jsonify(a)
    return render_template('code_page.html', title='Запуск кода', form=form)


def check_image(img_url):
    # Автомодерация изображений, перед тем, как поставить их на обложку проекта
    url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelUrls/'

    headers = {'accept': 'application/x-www-form-urlencoded'}

    data = {'modelId': '353cea12-4dcc-47ee-b139-dd345157b17d', 'urls': [img_url]}

    response = requests.request('POST', url, headers=headers,
                                auth=requests.auth.HTTPBasicAuth(config.NANONETS_API_TOKEN, ''),
                                data=data).json()
    res = response['result']
    return not res['prediction'][0]["probability"] > 0.3


def main():
    api.add_resource(gaduka_api.GadukaRunCodeApi, "/api/v1/engine")
    app.run(port=80, host='127.0.0.1')


if __name__ == '__main__':
    main()
