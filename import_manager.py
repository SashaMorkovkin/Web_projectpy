import os
import datetime as dt
from random import randint
from PIL import Image

from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import vk_api

from forms.vk_auth import AuthForm
from forms.user import LoginForm, RegisterForm, EditProfileForm
from forms.quizes import AddQuest, AddQuiz
from forms.search import Search
from forms.photo import UploadPhoto

from data import db_session
from data.users import User
from data.questions import Questions
from data.category import Category
from data.quezes import Quezes


def my_page_render(template, **kwargs):
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
    image = Image.open(
        f'{os.curdir}/{url_for("static", filename=f"images/{current_user.id}/preavatar.png")}')
    width, height = image.size
    cropsize = ((width - min(image.size)) // 2,
                (height - min(image.size)) // 2,
                (width + min(image.size)) // 2,
                (height + min(image.size)) // 2)
    im1 = image.crop(cropsize)
    im1.save(f'{os.curdir}/{url_for("static", filename=f"images/{current_user.id}/avatar.png")}')
