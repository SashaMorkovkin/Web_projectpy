from import_manager import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)


# Сбор ошибок (не авторизован, страница не найдена, нет доступа)
# и пересылание пользователя на нужные страницы.


@app.errorhandler(401)
def get_login(error):
    return redirect('/login')


@app.errorhandler(404)
def not_found(error):
    if ('The requested URL was not found on the server. If you entered the URL manually please '
            'check your spelling and try again.') == error.description:
        return my_page_render('error_handler.html', message='WORK IN PROGRESS')
    else:
        return my_page_render('error_handler.html', message=error)


@app.errorhandler(403)
def not_found(error):
    return my_page_render('error_handler.html', message=error)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def mainpage():
    """Главная страница сервера.
    Тут отбираются квизы для таких разделов как:
        -наиболее просматриваемые;
        -квизы от тех на кого вы подписаны."""
    white_list = get_whitelist()
    if current_user.is_authenticated:
        followingid = [i.id for i in current_user.following]
        by_friends = white_list.filter(Quezes.authorid.in_(followingid))
    else:
        by_friends = []
    most_passed = white_list.order_by(Quezes.passed.desc()).limit(10).all()
    return my_page_render('first_list.html', most_passed=most_passed, by_friends=by_friends)


@app.route('/all_quezes')
def all_quezes():
    """Страница со списком всех квизов"""
    return my_page_render('all_quezes.html', quezes=get_whitelist().all())


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Функция для регистрации"""
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
        user.avatar = f'images/{current_user.id}/avatar.png'
        db_sess.commit()
        # Пользователь сразу логинится, создается его папка галереи,
        # получает аватар из папки static/images/default, если папка с его id уже существует
        # (в случае удаления пользоваетля с таким же id из бд) она удаляется.
        if os.path.isdir(f'{os.curdir}/static/images/{current_user.id}'):
            shutil.rmtree(f"{os.curdir}/static/images/{current_user.id}")
        os.mkdir(f'static/images/{current_user.id}')
        shutil.copyfile(f"{os.curdir}/static/images/default/avatar.jpg",
                        f"{os.curdir}/static/images/{current_user.id}/avatar.png")
        return redirect('/')
    return my_page_render('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция авторизации на сайте"""
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
    """Главная функция сего проекта, создание квиза."""
    sess = db_session.create_session()
    if not quizid:
        # Проверка на наличие у пользователя 'черновика',
        # в случае отсутствия, генерирует uid и создает новый объект класса Quezes.
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
            # Функция сохранения 'черновика' квиза,
            # для последующего изменения аватара/добавления вопроса
            # или же чтобы сохранить на будущее.
            quiz.title = form.title.data
            quiz.description = form.description.data
            quiz.mode = form.mode.data
            quiz.pointsfge = form.pointsfge.data
            quiz.goodend = form.goodend.data
            quiz.badend = form.badend.data
            quiz.categories.clear()
            if int(form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category1.data))
            if int(form.category2.data) and form.category2.data != form.category1.data:
                quiz.categories.append(sess.query(Category).get(form.category2.data))
            if (int(form.category3.data) and form.category3.data != form.category2.data and
                    form.category3.data != form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category3.data))
            sess.commit()
            sess.close()
            return redirect(f'/newquiz/{quizid}')
        if form.validate_on_submit():
            # Функция окончательной валидации квиза и его публикация
            if not quiz.questions:
                return my_page_render('add_quiz.html',
                                      form=form,
                                      quiz=quiz,
                                      message='Добавьте хотя бы один вопрос!')
            quiz.title = form.title.data
            quiz.description = form.description.data
            quiz.mode = form.mode.data
            quiz.pointsfge = form.pointsfge.data
            quiz.goodend = form.goodend.data
            quiz.badend = form.badend.data
            quiz.categories.clear()
            if int(form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category1.data))
            if int(form.category2.data) and form.category2.data != form.category1.data:
                quiz.categories.append(sess.query(Category).get(form.category2.data))
            if (int(form.category3.data) and form.category3.data != form.category2.data and
                    form.category3.data != form.category1.data):
                quiz.categories.append(sess.query(Category).get(form.category3.data))
            quiz.publicated = True
            quiz.create = dt.datetime.now()
            sess.commit()
            sess.close()
            return redirect('/')
        if not quiz:
            # Создание квиза при отсутствии черновика.
            quiz = Quezes(
                id=quizid,
                authorid=current_user.id
            )
            sess.add(quiz)
            sess.commit()
        # Загрузка данных из черновика.
        form.title.data = quiz.title
        form.description.data = quiz.description
        form.pointsfge.data = quiz.pointsfge
        form.goodend.data = quiz.goodend
        form.badend.data = quiz.badend
        if len(quiz.categories) > 0:
            form.category1.data = str(quiz.categories[0].id)
        if len(quiz.categories) > 1:
            form.category2.data = str(quiz.categories[1].id)
        if len(quiz.categories) > 2:
            form.category3.data = str(quiz.categories[2].id)
        if not is_author(current_user.id, quizid):
            return abort(403, "It's not yours!!")
        # Получение фото для работы dropdown с выбором обложки опроса.
        photos = []
        directory = f'static/images/{current_user.id}'
        for image in os.listdir(directory):
            photos.append({'url': f'{directory[7:]}/{image}', 'number': str(image)})
        # Получение макс. значения range field.
        points = sum([i.koeff for i in quiz.questions])
        return my_page_render('add_quiz.html', form=form, quiz=quiz, photos=photos,
                              points=points)


@app.route('/newquiz/<int:quizid>/select_cover/<photo>')
def select_cover(quizid, photo):
    """ Функция смены обложки. """
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    sess = db_session.create_session()
    quiz = sess.query(Quezes).get(quizid)
    if photo:
        quiz.cover = f'images/{current_user.id}/{photo}'
        sess.commit()
        sess.close()
        return redirect(f'/newquiz/{quizid}')


@app.route('/delquiz/<int:quizid>', methods=['GET', 'POST'])
@login_required
def del_quiz(quizid):
    """ Удаление квиза с подтверждением. """
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    if request.method == "POST":
        sess = db_session.create_session()
        sess.delete(sess.query(Quezes).get(quizid))
        sess.commit()
        sess.close()
        return redirect('/')
    return my_page_render('sure.html', id=quizid)


@app.route('/newquiz/<int:quizid>/newquest', methods=['GET', 'POST'])
@login_required
def add_quest(quizid):
    """Добавление вопроса к квизу."""
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
    """Изменение вопроса"""
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
    """Удаление вопроса"""
    if not is_author(current_user.id, quizid):
        return abort(403, "It's not yours!!")
    sess = db_session.create_session()
    question = sess.query(Questions).get(questid)
    if not question:
        return abort(404, f'Unknown question id: {questid}')
    sess.delete(question)
    sess.commit()
    return redirect(f'/newquiz/{quizid}')


@app.route('/quiz/<int:quizid>/info')
def quizinfo(quizid):
    """ Функция отображающая всю доступную информацию по квизу. """
    sess = db_session.create_session()
    quiz = get_whitelist().get(quizid).first()
    if not quiz:
        return abort(404, f"Quiz {quizid} not found or it's private.")
    quiz = sess.query(Quezes).get(quizid)
    return my_page_render('quizinfo.html', quiz=quiz)


@app.route('/quiz/<int:quizid>', methods=["POST", "GET"])
def quiz(quizid):
    """ Прохождение квиза. """
    sess = db_session.create_session()
    quiz = get_whitelist().filter(Quezes.id == quizid).first()
    if not quiz:
        return abort(404, f"Quiz {quizid} not found or it's private.")
    quiz = sess.query(Quezes).get(quizid)
    if request.method == "POST":
        form = dict(request.form)
        points = 0
        if len(form) != len(quiz.questions):
            return my_page_render('quiz.html',
                                  quiz=quiz,
                                  message='Вы не ответили на все вопросы. ОТВЕЧАЙТЕ ПО НОВОЙ БУГАГА'
                                  )
        for i in range(len(quiz.questions)):
            points += (int(eval(f'quiz.questions[{i}].points{form[list(form.keys())[0]]}')) *
                       quiz.questions[i].koeff * 0.01)
        # Неавторизованные пользователи не могут накручивать просмотры.
        if current_user.is_authenticated:
            quiz.passed += 1
        sess.commit()
        return redirect(f'/quiz/{quizid}/end/{points}')
    return my_page_render('quiz.html', quiz=quiz)


@app.route('/quiz/<int:quizid>/end/<float:points>')
def end(quizid, points):
    """ Выдача результата на основе полученных баллов за квиз."""
    sess = db_session.create_session()
    quiz = sess.query(Quezes).get(quizid)
    if not quiz:
        return abort(404, f'Quiz {quizid} not found.')
    if points >= quiz.pointsfge:
        return my_page_render('result.html', mode=True, points=points, goodend=quiz.goodend)
    else:
        return my_page_render('result.html', mode=False, points=points, badend=quiz.badend)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    """Функция для просмотра своего профиля"""
    sess = db_session.create_session()
    quizes = sess.query(Quezes).filter(Quezes.authorid == current_user.id).all()
    return my_page_render('my_profile.html', quizes=quizes)


@app.route('/profile/<int:userid>', methods=['GET', 'POST'])
def profile(userid):
    """Отображает профиль другого пользователя предварительно проверив его настройки приватности."""
    if current_user.is_authenticated and userid == current_user.id:
        # Если usrid в url был ваш, то отправляет вас в ваш профиль.
        return redirect('/profile')
    sess = db_session.create_session()
    user = sess.query(User).get(userid)
    if not user:
        return abort(404, f'User {userid} not found')
    if user.is_private == 'True':
        # 'True' означает полностью приватный профиль.
        return abort(403, "It's private")
    if user.is_private == 'NS':
        # 'Ns' означает что к профилю доступ имеют те на кого ты подписан.
        if current_user.is_authenticated and current_user.id not in [i.id for i in user.following]:
            return abort(403, "It's private")
        if not current_user.is_autheticated:
            return abort(403, "It's private")
        quizes = get_whitelist().filter(Quezes.authorid == user.id).all()
        is_friend = current_user.id in [i.id for i in user.followers]
        return my_page_render('profile.html', quizes=quizes, user=user, is_friend=is_friend)
    # 'False' установленый по умолчанию означает полностью открытый профиль.
    quizes = get_whitelist().filter(Quezes.authorid == user.id).all()
    is_friend = current_user.is_authenticated and current_user.id in [i.id for i in user.followers]
    return my_page_render('profile.html', quizes=quizes, user=user, is_friend=is_friend)


@app.route('/set_avatar', methods=['POST', 'GET'])
@login_required
def edit_avatar():
    """ Функция смены аватара """
    # Для edit_avatar и upload_photo используется одна форма.
    form = UploadPhoto()
    if form.validate_on_submit():
        form.image.data.save(f'static/images/{current_user.id}/preavatar.png')
        # Вызов функции-обрезчика фото.
        make_avatar()
        os.remove(
            f'{os.curdir}/static/images/{current_user.id}/preavatar.png')
        sess = db_session.create_session()
        user = sess.get(User, current_user.id)
        user.vk_photo = False
        user.avatar = f'images/{current_user.id}/avatar.png'
        sess.commit()
        return redirect('/profile')
    else:
        return my_page_render('upload.html', form=form, mode='профиля')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ Функция изменения данных о себе: возраста, имени, приватности и своего описания. """
    editform = EditProfileForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            editform.name.data = user.name
            editform.about.data = user.about
            editform.age.data = user.age
            editform.is_private.data = user.is_private
        else:
            abort(404, 'Unknown found your profile')
    if editform.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = editform.name.data
            user.about = editform.about.data
            user.age = editform.age.data
            user.is_private = editform.is_private.data
            db_sess.commit()
            return redirect('/profile')
        else:
            abort(404, 'Unknown found your profile')
    return my_page_render('edit_profile.html', form=editform)


@app.route('/subscribe/<userid>')
@login_required
def subscribe(userid):
    """ Функция добавления пользователя в свои подписки. """
    sess = db_session.create_session()
    user = sess.query(User).get(userid)
    user.followers.append(sess.query(User).get(current_user.id))
    sess.commit()
    return redirect(f'/profile/{userid}')


@app.route('/unsubscribe/<userid>')
@login_required
def unsubscribe(userid):
    """ Функция убирания пользователя из своих подписок. """
    sess = db_session.create_session()
    user = sess.query(User).get(userid)
    user.followers.remove(sess.query(User).get(current_user.id))
    sess.commit()
    return redirect(f'/profile/{userid}')


def vk_auth():
    form = Auth2()
    if form.validate_on_submit():
        key = form.key.data
        return key
    return my_page_render('auth2.html', form=form)


def auth_handler():
    key = vk_auth()
    remember_device = True
    return key, remember_device


@app.route('/auth', methods=['GET', 'POST'])
@login_required
def auth():
    form = AuthForm()
    message = ''
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.vk_id == current_user.vk_id).all()
        if users and current_user.vk_id:
            message = 'Вы уже авторизованы'
            return my_page_render('vk_auth.html', form=form, message=message)
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
        user.avatar = f"{response[0]['crop_photo']['photo']['sizes'][-2]['url']}"
        user.name = f"{response[0]['first_name']} {response[0]['last_name']}"
        user.vk_photo = True
        user.vk_id = response[0]['id']
        db_sess.commit()
        return redirect('/profile')
    return my_page_render('vk_auth.html', form=form, message=message)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """ Функция поиска. """
    if request.method == 'GET':
        quest = request.args['field']
        quest_method = request.args.get('user', request.args.get('quiz'))
        sess = db_session.create_session()
        # В зависимости от метода выдает разные типы данных.
        if quest_method == 'Юзер':
            users = sess.query(User).filter(User.name.like(f'%{quest}%'))
            if current_user.is_authenticated:
                users = [{'user': i,
                          'is_friend': current_user.id in [j.id for j in i.followers]}
                         for i in users]
                users.sort(key=lambda x: -x['is_friend'])
            else:
                users = [{'user': i} for i in users]
            return my_page_render('search.html', quest=quest, quest_method=quest_method,
                                  rez=users)
        if quest_method == 'Опрос':
            # Тут также проверяется приватность квиза.
            quezes = get_whitelist().filter(Quezes.title.like(f'%{quest}%')).all()
            return my_page_render('search.html', quest=quest, quest_method=quest_method,
                                  quezes=quezes)


@app.route('/album')
@login_required
def my_gallery():
    """Функция отображения всех фото из вашей папки-галереи """
    urls = []
    directory = f'static/images/{current_user.id}'
    for image in os.listdir(directory):
        urls.append({'img': url_for('static', filename=f'{directory[7:]}/{image}'),
                     'number': image})
    return my_page_render('album.html', urls=urls, user=current_user)


@app.route('/album/<int:userid>')
def user_gallery(userid):
    """Функция отображения фотографий другого пользователя"""
    if current_user.is_authenticated and userid == current_user.id:
        # Если ваш id и id из url совпадают, пересылает на вашу галерею.
        return redirect('/album')
    sess = db_session.create_session()
    user = sess.query(User).get(userid)
    # Тут также проверяется приватность пользовательского аккаунта.
    if not user:
        return abort(404, f'User {userid} not found')
    if user.is_private == 'True':
        return abort(403, "It's private")
    if user.is_private == 'NS':
        if current_user.is_authenticated and current_user.id not in [i.id for i in user.following]:
            return abort(403, "It's private")
        if not current_user.is_autheticated:
            return abort(403, "It's private")
    urls = []
    directory = f'static/images/{userid}'
    if os.path.isdir(directory):
        for image in os.listdir(directory):
            urls.append(url_for('static', filename=f'{directory[7:]}/{image}'))
    return my_page_render('album.html', urls=urls, user=user)


@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    """ Загрузка фотографии в галерею """
    form = UploadPhoto()
    if form.validate_on_submit():
        last = os.listdir(f'static/images/{current_user.id}')[-1].split('.')[0]
        # Определяет номер последнего изображения и сохраняет новое с последующим номером
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


@app.route('/del_photo/<name>')
@login_required
def del_photo(name):
    """Удаление фото по его имени в папке пользователя."""
    if os.path.isfile(f'static/images/{current_user.id}/{name}'):
        try:
            os.remove(f'{os.curdir}/static/images/{current_user.id}/{name}')
        except Exception as ex:
            return abort(404, ex)
        if name == 'avatar.png':
            shutil.copyfile(f"{os.curdir}/static/images/default/avatar.jpg",
                            f"{os.curdir}/static/images/{current_user.id}/avatar.png")
        sess = db_session.create_session()
        # Всем квизам где использовалось фото присваивается стандартная обложка.
        quezes = sess.query(Quezes).filter(
            Quezes.cover == f'images/{current_user.id}/{name}').all()
        for quiz in quezes:
            quiz.cover = 'images/default/cover.png'
        sess.commit()
        return redirect('/album')
    else:
        return abort(404, 'File not found')


@app.route('/category/<int:catid>')
def category(catid):
    """ Все доступные квизы с категорией """
    sess = db_session.create_session()
    cat = sess.query(Category).get(catid)
    if not cat:
        return abort(404, f'Category {catid} not found')
    else:
        quezes = []
        prequezes = get_whitelist().all()
        print(prequezes)
        for quiz in prequezes:
            ids = [i.id for i in quiz.categories]
            if cat.id in ids:
                quezes.append(quiz)
        return my_page_render('category.html', quezes=quezes, cat=cat)


def main():
    # connect to Database
    if not os.path.isdir("db"):
        os.mkdir("db")
    db_session.global_init('db/blogs.db')
    sess = db_session.create_session()
    # set actuality ategories to AddQuiz form
    categories = [(0, '')]
    for cat in sess.query(Category).all():
        categories.append((cat.id, cat.name))
    sess.close()
    AddQuiz.set_categories(categories)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
