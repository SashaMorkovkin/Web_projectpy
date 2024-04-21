import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.users import User
from data.quezes import Quezes
import pymorphy2
import json

TOKEN = ('vk1.a.iKxIo89g-nr1A5X_-fhiztJ7OCwMbuV2hugyx3t47_KDN5ZbNOe2NT8aw5dj5PHtqB9LbH2ZKMqcqLC8eWe'
         'nqmPSVfkaaoE7pD87NdwWXISA8eEu0fWoQWnvA16rx9ABQy6qu22uR6ZKyz3NAJ-cOADRatWut_6MTrC9w9_Y6r02'
         'Oil5hEnW17S58U_x_TMmw8yVuI5pW7YCJt2RKJM6sQ')
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app")
morph = pymorphy2.MorphAnalyzer()
com = morph.parse('опрос')[0]


def bot():
    f_toggle: bool = False
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, '225254028')
    db_sess = db_session.create_session()
    keyboard_1 = VkKeyboard(one_time=True, inline=True)
    keyboard_1.add_callback_button(
        label="Покажи pop-up сообщение",
        color=VkKeyboardColor.SECONDARY,
        payload={"type": "show_snackbar", "text": "Это исчезающее сообщение на экране"},
    )
    keyboard_1.add_line()
    keyboard_1.add_callback_button(
        label="Откртыть Url",
        color=VkKeyboardColor.POSITIVE,
        payload={"type": "open_link", "link": "https://vk.com/dev/bots_docs_5"},
    )
    for event in longpoll.listen():
        vk = vk_session.get_api()
        if event.obj.message["text"] != "":
            member = vk.groups.isMember(group_id=225254028, user_id=event.obj.message['from_id'])
            if member == 0:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"Привет, {vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}! Для прохождения опросов нужно подписаться на бота👆",
                                 random_id=random.randint(0, 2 ** 64))
            elif event.type == VkBotEventType.GROUP_JOIN and vk.users.get(user_id=event.object.user_id):
                vk.messages.send(user_id=event.object.user_id,
                                 message=f"{vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']}, нет аккаунта? Зарегистрируйте его по этой ссылке: *ссылка*",
                                 random_id=random.randint(0, 2 ** 64))
                print(
                    f"пользователь {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']} присоединился!")
            elif event.type == VkBotEventType.MESSAGE_NEW:
                us = db_sess.query(User).filter(User.vk_id == event.obj.message['from_id']).first()
                user_id = us.id
                quizes = db_sess.query(Quezes).filter(Quezes.authorid == user_id).all()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"{vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}, ты создал {len(quizes)} {com.make_agree_with_number(len(quizes)).word}.",
                                 random_id=random.randint(0, 2 ** 64))