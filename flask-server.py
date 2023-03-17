from flask import Flask, render_template
import random

app = Flask(__name__)


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
    a = ("http://127.0.0.1:8080/static/img/gaduka-icon.png", "http://127.0.0.1:8080/static/img/tg-icon.png",
         "http://127.0.0.1:8080/static/img/result_img_2.png", "http://127.0.0.1:8080/static/img/result_img_1.png")
    b = ("Проект", "Эксперимент", "eagnaiegu;g")
    projects = enumerate(((f"{random.choice(b)} {j}", random.choice(a)) for j in range(30)))
    if not exist_user:
        return render_template("user_error_page.html", my_username=my_username, logged=logged)

    return render_template('user_page.html', my_username=my_username, logged=logged,
                           user_page_name=username, projects=projects, title=f"Профиль {my_username}")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
