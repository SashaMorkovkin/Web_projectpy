import os
from flask import Flask, render_template, redirect, request, make_response, url_for, abort
import datetime as dt
import vk_api
from random import randint
from forms.vk_auth import AuthForm
from forms.user import LoginForm, RegisterForm, EditProfileForm
from forms.quizes import AddQuest, AddQuiz
from forms.search import Search
from data import db_session
from data.users import User
from data.questions import Questions
from data.category import Category
from data.quezes import Quezes
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
    search_form = Search()
    if current_user.is_authenticated:
        kwargs['avatar'] = url_for('static', filename=current_user.avatar)
    return render_template(template,
                           categories=categories,
                           title='IQuiz',
                           search=search_form,
                           **kwargs)


@app.errorhandler(401)
def get_login(error):
    print(error)
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def mainpage():
    sess = db_session.create_session()
    quizes = sess.query(Quezes).all()
    return my_page_render('first_list.html', quizes=quizes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return my_page_render('register.html', form=form,
                                  message='Email уже зарегистрирован')
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        if os.path.isdir(f'static/images/{user.id}'):
            os.remove(f'static/images/{user.id}')
        os.mkdir(f'static/images/{user.id}')
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
        return my_page_render('login.html', message="Неправильный логин или пароль",
                              form=form)
    return my_page_render('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/newquiz/<int:quizid>')
@app.route('/newquiz')
@login_required
def add_quiz(quizid=0):
    sess = db_session.create_session()
    if not quizid:
        quizesids = sess.query(Quezes.id).all()
        newid = randint(1, 100001)
        while newid in quizesids:
            newid = randint(1, 100001)
        else:
            return redirect(f'/newquiz/{newid}')
    else:
        form = AddQuiz()
        return my_page_render('add_quiz.html', form=form, id=quizid)


@app.route('/newquiz/<int:quizid>/newquest', methods=['GET', 'POST'])
@login_required
def add_quest(quizid):
    form = AddQuest()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = Questions(
            title=form.title.data,
            answer1=form.answer1.data,
            answer2=form.answer2.data,
            answer3=form.answer3.data,
            answer4=form.answer4.data,
            answer5=form.answer5.data,
            answer6=form.answer6.data
        )
        question.quizid = quizid
        db_sess.commit()
        return redirect('/')
    return my_page_render('add_question.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    return my_page_render('my_profile.html')


@app.route('/photo', methods=['POST', 'GET'])
def change_avatar():
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        image = request.files['file']
        image.save(f'static/images/default/avatar.jpg')
        user.avatar = f'static/images/default/avatar.jpg'


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    editform = EditProfileForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            editform.name.data = user.name
            editform.about.data = user.about
            editform.age.data = user.age
        else:
            abort(404)
    if editform.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = editform.name.data
            user.about = editform.about.data
            user.age = editform.age.data
            db_sess.commit()
            return redirect('/profile')
        else:
            abort(404)
    return my_page_render('edit_profile.html', form=editform)


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


@app.route('/auth', methods=['GET', 'POST'])
@login_required
def auth():
    form = AuthForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        login = form.login.data
        password = form.password.data
        vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return
        vk = vk_session.get_api()
        response = vk.users.get(fields="first_name, last_name, status, crop_photo")
        print(response)
        if response[0]['status']:
            user.about = response[0]['status']
        print(response[0]['crop_photo']['photo']['sizes'][-2])
        user.avatar = response[0]['crop_photo']['photo']['sizes'][-2]['url']
        user.name = f"{response[0]['first_name']} {response[0]['last_name']}"
        db_sess.commit()
        return redirect('/profile')
    return my_page_render('vk_auth.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        quest = request.args['field']
        quest_method = request.args.get('user', request.args.get('quiz'))
        sess = db_session.create_session()
        if quest_method == 'Юзер':
            users = sess.query(User).filter(User.name.like(f'%{quest}%'))
            return my_page_render('search.html', quest=quest, quest_method=quest_method,
                                  rez=users)
        if quest_method == 'Опрос':
            quizes = sess.query(Quezes).filter(Quezes.title.like(f'%{quest}%'))
            return my_page_render('search.html', quest=quest, quest_method=quest_method,
                                  rez=quizes)


@app.route('/album')
@login_required
def my_gallery():
    urls = []
    directory = f'static/images/{current_user.id}'
    if os.path.isdir(directory):
        for image in os.listdir(directory):
            urls.append(url_for('static', filename=f'{directory[7:]}/{image}'))
    return my_page_render('album.html', urls=urls, user=current_user)


@app.route('/album/<int:userid>')
def user_gallery(userid):
    if current_user.is_authenticated and userid == current_user.id:
        return redirect('/album')
    sess = db_session.create_session()
    user = sess.query(User).get(userid)
    if not user:
        return make_response(404, 'unknown user id')
    urls = []
    directory = f'static/images/{userid}'
    if os.path.isdir(directory):
        for image in os.listdir(directory):
            urls.append(url_for('static', filename=f'{directory[7:]}/{image}'))
    return my_page_render('album.html', urls=urls, user=user)


def main():
    if not os.path.isdir("db"):
        os.mkdir("db")
    db_session.global_init('db/blogs.db')
    sess = db_session.create_session()
    categories = [(0, '')]
    for cat in sess.query(Category).all():
        categories.append((cat.id, cat.name))
    AddQuiz.set_categories(categories)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
