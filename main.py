from import_manager import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)


def is_author(userid: int, quizid: int) -> bool:
    sess = db_session.create_session()
    quiz = sess.query(Quezes).get(quizid)
    if userid == quiz.authorid or userid == 1:
        return True
    else:
        return False


@app.errorhandler(401)
def get_login(error):
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def mainpage():
    sess = db_session.create_session()
    quizes = sess.query(Quezes).filter(Quezes.authorid == current_user.id)
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
        if os.path.isdir(url_for('static', filename=f'images/{user.id}')):
            os.rmdir(url_for('static', filename=f'images/{user.id}'))
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


@app.route('/newquiz/<int:quizid>', methods=['GET', 'POST'])
@app.route('/newquiz')
@login_required
def add_quiz(quizid=0):
    sess = db_session.create_session()
    if not quizid:
        draft = sess.query(Quezes.id).filter(Quezes.authorid == current_user.id,
                                             Quezes.publicated == 0).first()
        if draft:
            return redirect(f'/newquiz/{draft[0]}')
        else:
            quizesids = sess.query(Quezes.id).all()
            newid = randint(1, 100001)
            while (newid,) in quizesids:
                newid = randint(1, 100001)
            else:
                return redirect(f'/newquiz/{newid}')
    else:
        form = AddQuiz()
        quiz = sess.query(Quezes).get(quizid)
        if form.save.data:
            quiz.title = form.title.data
            quiz.description = form.description.data
            quiz.mode = form.mode.data
            quiz.categories.clear()
            if int(form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category1.data))
            if int(form.category2.data) and form.category2.data != form.category1.data:
                quiz.categories.append(sess.query(Category).get(form.category2.data))
            if (int(form.category3.data) and form.category3.data != form.category2.data and
                    form.category3.data != form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category3.data))
            sess.commit()
            return redirect(f'/newquiz/{quizid}')
        if form.validate_on_submit():
            print(form.save.data)
            if not quiz.questions:
                return my_page_render('add_quiz.html',
                                      form=form,
                                      quiz=quiz,
                                      message='Добавьте хотя бы один вопрос!')
            quiz.title = form.title.data
            quiz.description = form.description.data
            quiz.mode = form.mode.data
            quiz.categories.clear()
            if int(form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category1.data))
            if int(form.category2.data) and form.category2.data != form.category1.data:
                quiz.categories.append(sess.query(Category).get(form.category2.data))
            if (int(form.category3.data) and form.category3.data != form.category2.data and
                    form.category3.data != form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category3.data))
            quiz.publicated = True
            sess.commit()
            return redirect('/')
        if not quiz:
            quiz = Quezes(
                id=quizid,
                authorid=current_user.id
            )
            sess.add(quiz)
            sess.commit()
        else:
            form.title.data = quiz.title
            form.description.data = quiz.description
            if len(quiz.categories) > 0:
                form.category1.data = str(quiz.categories[0].id)
            if len(quiz.categories) > 1:
                form.category2.data = str(quiz.categories[1].id)
            if len(quiz.categories) > 2:
                form.category3.data = str(quiz.categories[2].id)
        if not is_author(current_user.id, quizid):
            return abort(403, "It's not yours!!")
        photos = []
        directory = f'static/images/{current_user.id}'
        for image in os.listdir(directory):
            photos.append(f'{directory[7:]}/{image}')
        return my_page_render('add_quiz.html', form=form, quiz=quiz, photos=photos)


@app.route('/newquiz/<int:quizid>/delete', methods=['GET', 'POST'])
@app.route('/newquiz')
@login_required
def del_quiz(quizid):
    if request.method == "POST":
        sess = db_session.create_session()
        sess.delete(sess.query(Quezes).get(quizid))
        sess.commit()
        return redirect('/')
    return my_page_render('sure.html', id=quizid)


@app.route('/newquiz/<int:quizid>/newquest', methods=['GET', 'POST'])
@login_required
def add_quest(quizid):
    form = AddQuest()
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    if form.validate_on_submit():
        sess = db_session.create_session()
        question = Questions(
            title=form.title.data,
            answer1=form.answer1.data,
            points1=form.points1.data,
            answer2=form.answer2.data,
            points2=form.points2.data,
            koeff=form.koeff.data,
            quizid=quizid
        )
        forsum = [form.points1.data, form.points2.data]
        if form.answer3.data:
            question.answer3, question.points3 = form.answer3.data, form.points3.data
            forsum.append(form.points3.data)
        if form.answer4.data:
            question.answer4, question.points4 = form.answer4.data, form.points4.data
            forsum.append(form.points4.data)
        if form.answer5.data:
            question.answer5, question.points5 = form.answer5.data, form.points5.data
            forsum.append(form.points5.data)
        if form.answer6.data:
            question.answer6, question.points6 = form.answer6.data, form.points6.data
            forsum.append(form.points6.data)
        if sum(forsum) != 100:
            return my_page_render(
                'add_question.html',
                form=form,
                message='Сумма очков у существующих ответов должна быть равна 100.'
            )
        sess.add(question)
        sess.commit()
        return redirect(f'/newquiz/{quizid}')
    return my_page_render('add_question.html', form=form)


@app.route('/newquiz/<int:quizid>/editquest/<int:questid>', methods=['GET', 'POST'])
@login_required
def edit_quest(quizid, questid):
    form = AddQuest()
    sess = db_session.create_session()
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    if request.method == 'GET':
        question = sess.query(Questions).get(questid)
        if question:
            form.title.data = question.title
            form.answer1.data, form.points1.data = question.answer1, question.points1
            form.answer2.data, form.points2.data = question.answer2, question.points2
            form.answer3.data, form.points3.data = question.answer3, question.points3
            form.answer4.data, form.points4.data = question.answer4, question.points4
            form.answer5.data, form.points5.data = question.answer5, question.points5
            form.answer6.data, form.points6.data = question.answer6, question.points6
            form.koeff.data = question.koeff
        else:
            return abort(404, f'Unknown question id: {questid}')
    if form.validate_on_submit():
        question = sess.query(Questions).get(questid)
        if question:
            question.title = form.title.data
            question.answer1, question.points1 = form.answer1.data, form.points1.data
            question.answer2, question.points2 = form.answer2.data, form.points2.data
            question.koeff = form.koeff.data
            forsum = [form.points1.data, form.points2.data]
            if form.answer3.data:
                question.answer3, question.points3 = form.answer3.data, form.points3.data
                forsum.append(form.points3.data)
            if form.answer4.data:
                question.answer4, question.points4 = form.answer4.data, form.points4.data
                forsum.append(form.points4.data)
            if form.answer5.data:
                question.answer5, question.points5 = form.answer5.data, form.points5.data
                forsum.append(form.points5.data)
            if form.answer6.data:
                question.answer6, question.points6 = form.answer6.data, form.points6.data
                forsum.append(form.points6.data)
            if sum(forsum) != 100:
                return my_page_render(
                    'add_question.html',
                    form=form,
                    message='Сумма очков у существующих ответов должна быть равна 100.'
                )
            sess.commit()
            return redirect(f'/newquiz/{quizid}')
        else:
            return abort(404, f'Unknown question id: {questid}')
    return my_page_render('add_question.html', form=form)


@app.route('/newquiz/<int:quizid>/delquest/<int:questid>')
@login_required
def del_quest(quizid, questid):
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    sess = db_session.create_session()
    question = sess.query(Questions).get(questid)
    if not question:
        return abort(404, f'Unknown question id: {questid}')
    sess.delete(question)
    sess.commit()
    return redirect(f'/newquiz/{quizid}')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    return my_page_render('my_profile.html')


@app.route('/set_avatar', methods=['POST', 'GET'])
def edit_avatar():
    form = UploadPhoto()
    if form.validate_on_submit():
        form.image.data.save(f'static/images/{current_user.id}/preavatar.png')
        make_avatar()
        os.remove(
            f'{os.curdir}/{url_for("static", filename=f"images/{current_user.id}/preavatar.png")}')
        sess = db_session.create_session()
        user = sess.get(User, current_user.id)
        user.avatar = f'images/{current_user.id}/avatar.png'
        sess.commit()
        return redirect('/profile')
    else:
        return my_page_render('upload.html', form=form, mode='профиля')


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
            abort(404, 'Unknown found your profile')
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
            abort(404, 'Unknown found your profile')
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
        user.avatar = response[0]['crop_photo']['photo']['sizes'][-2]['url']
        user.name = f"{response[0]['first_name']} {response[0]['last_name']}"
        user.vk_id = response[0]['id']
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
        return abort(404, 'unknown user id')
    urls = []
    directory = f'static/images/{userid}'
    if os.path.isdir(directory):
        for image in os.listdir(directory):
            urls.append(url_for('static', filename=f'{directory[7:]}/{image}'))
    return my_page_render('album.html', urls=urls, user=user)


@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    form = UploadPhoto()
    if form.validate_on_submit():
        last = os.listdir(f'static/images/{current_user.id}')[-1].split('.')[0]
        print(last)
        if last != 'avatar':
            last = int(last)
        else:
            try:
                last = os.listdir(f'static/images/{current_user.id}')[-2].split('.')[0]
            except Exception:
                last = 0
            else:
                last = int(last)
        form.image.data.save(f'static/images/{current_user.id}/{last + 1}.png')
        return redirect('/album')
    return my_page_render('upload.html', form=form, mode='в альбом')


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
