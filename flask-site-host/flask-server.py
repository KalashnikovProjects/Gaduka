import json
from datetime import timedelta

from flask import Flask, render_template, request, session, make_response, redirect, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, login_manager
import hashlib
import hmac
import config
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '/mops/delete/up/pack/super214jmi3rg4nsnfaqta/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    days=3650
)
# login_manager = LoginManager()
# login_manager.init_app(app)


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
    logged = False
    my_username = 'Kalashnik'

    exist_user = True
    a = ("http://127.0.0.1:8080/static/img/gaduka-icon.png", "http://127.0.0.1:8080/static/img/tg-icon.png",
         "http://127.0.0.1:8080/static/img/result_img_2.png", "http://127.0.0.1:8080/static/img/result_img_1.png")
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

    secret_key = hashlib.sha256(config.token.encode('utf-8')).digest()
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
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@app.route('/login_error')
def login_error_page():
    return render_template('login_error_page.html', title="Ошибка при входе в аккаунт")


if __name__ == '__main__':
    app.run(port=80, host='127.0.0.1')
