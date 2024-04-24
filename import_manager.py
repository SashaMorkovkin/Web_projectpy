import os
import datetime as dt
from random import randint
from PIL import Image

from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms.validators import NumberRange

import vk_api

from forms.vk_auth import AuthForm, Auth2
from forms.user import LoginForm, RegisterForm, EditProfileForm
from forms.quizes import AddQuest, AddQuiz
from forms.search import Search
from forms.photo import UploadPhoto

from data import db_session
from data.users import User
from data.questions import Questions
from data.category import Category
from data.quezes import Quezes
import shutil


def my_page_render(template, **kwargs):
    '''Функция-декоратор для render_template(),
    тут загружаются все данные необходимые для base.html'''
    print(kwargs)
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    search_form = Search()
    return render_template(template,
                           categories=categories,
                           title='IQuiz',
                           search=search_form,
                           **kwargs)


def make_avatar():
    '''Функция для обрезания фото в квадрат при загрузке аватара'''
    image = Image.open(
        f'{os.curdir}/{url_for("static", filename=f"images/{current_user.id}/preavatar.png")}')
    width, height = image.size
    cropsize = ((width - min(image.size)) // 2,
                (height - min(image.size)) // 2,
                (width + min(image.size)) // 2,
                (height + min(image.size)) // 2)
    im1 = image.crop(cropsize)
    im1.save(f'{os.curdir}/{url_for("static", filename=f"images/{current_user.id}/avatar.png")}')


def get_whitelist():
    '''Возвращает квизы доступные для пользователя по настройкам приватности'''
    sess = db_session.create_session()
    if current_user.is_authenticated:
        followersid = [i.id for i in current_user.followers]
        white_list = sess.query(Quezes).filter(
            (Quezes.publicated) &
            ((Quezes.mode == 'forall') |
             (Quezes.authorid == current_user.id) |
             ((Quezes.authorid.in_(followersid)) & (Quezes.mode == 'forfriends'))))
    else:
        white_list = sess.query(Quezes).filter(Quezes.publicated & (Quezes.mode == 'forall'))
    return white_list


def is_author(userid: int, quizid: int) -> bool:
    '''Функция с говорящим названием'''
    sess = db_session.create_session()
    quiz = sess.query(Quezes).get(quizid)
    if userid == quiz.authorid or userid == 1:
        sess.close()
        return True
    else:
        sess.close()
        return False