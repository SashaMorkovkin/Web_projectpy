import os

from flask import Flask, render_template, redirect, request, make_response, url_for
from data import db_session
import datetime as dt
from forms.user import LoginForm, RegisterForm
from data.users import User
from data.questions import Questions
from forms.question import AddForm
from data.category import Category
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)


def my_page_render(template, **kwargs):
    print(kwargs)
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    if current_user.is_authenticated:
        kwargs['avatar'] = url_for('static', filename=current_user.avatar)
    return render_template(template, **kwargs, categories=categories, title='IQuiz')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return my_page_render('first_list.html')


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return my_page_render('register.html', title='Регистрация', form=form,
                                  message='Пароли разные')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return my_page_render('register.html', form=form, message='Пользователь уже существует')
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return my_page_render('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return my_page_render('login.html', message="Неправильный логин или пароль", form=form)
    return my_page_render('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/questions', methods=['GET', 'POST'])
@login_required
def add_news():
    form = AddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        questions = Questions(
            ask=request.json['ask'],
            question1=request.json['question1'],
            question2=request.json['question2'],
            question3=request.json['question3'],
            question4=request.json['question4'],
            is_private=request.json['is_private'],
        )
        current_user.questions.append(questions)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_question.html', title='добавить вопрос', form=form)


@app.route('/gallery/<int:userid>')
@app.route('/gallery/')
def gallery(userid=0):
    urls = []
    if userid:
        directory = f'static/images/{current_user.id}'
        if os.path.isdir(directory):
            for image in os.listdir(directory):
                urls.append(url_for('static', filename=f'{directory[7:]}/{image}'))
    return my_page_render('gallery.html', urls=urls)


def main():
    db_session.global_init('db/blogs.db')
    db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
