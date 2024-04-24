import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.users import User
from data.quezes import Quezes
import pymorphy2

TOKEN = ('vk1.a.iKxIo89g-nr1A5X_-fhiztJ7OCwMbuV2hugyx3t47_KDN5ZbNOe2NT8aw5dj5PHtqB9LbH2ZKMqcqLC8eWe'
         'nqmPSVfkaaoE7pD87NdwWXISA8eEu0fWoQWnvA16rx9ABQy6qu22uR6ZKyz3NAJ-cOADRatWut_6MTrC9w9_Y6r02'
         'Oil5hEnW17S58U_x_TMmw8yVuI5pW7YCJt2RKJM6sQ')
morph = pymorphy2.MorphAnalyzer()
com = morph.parse('опрос')[0]


def bot():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, '225254028')
    db_sess = db_session.create_session()
    for event in longpoll.listen():
        vk = vk_session.get_api()
        if event.type == VkBotEventType.GROUP_JOIN and vk.users.get(
                user_id=event.object.user_id):  # Уведомление о вступлении в группу
            vk.messages.send(user_id=event.object.user_id,
                             message=f"{vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']}, нет аккаунта? Зарегистрируйте его по этой ссылке: https://iquiz993zxc.glitch.me",
                             random_id=random.randint(0, 2 ** 64))
            print(
                f"пользователь {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']} присоединился!")
            vk.messages.send(user_id=event.object.user_id,
                             message=f"После регистрации вы можете узнать информацию об акааунте, написав 'инфо'",
                             random_id=random.randint(0, 2 ** 64))
        elif event.type == VkBotEventType.MESSAGE_NEW:
            member = vk.groups.isMember(group_id=225254028, user_id=event.obj.message['from_id'])
            print(event.obj.message['from_id'])
            if member == 0:  # если пользователь не является подписчиком сообщества
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"Привет, {vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}! Для прохождения опросов нужно подписаться на бота👆",
                                 random_id=random.randint(0, 2 ** 64))
            elif 'инфо' in event.obj.message['text'].lower():  # обработчик команды инфо
                us = db_sess.query(User).filter(User.vk_id == event.obj.message['from_id']).first()
                print(us)
                if us:  # если vk_id пользователя уже есть в бд
                    user_id = us.id
                    quizes = db_sess.query(Quezes).filter(Quezes.authorid == user_id).all()
                    passes = 0
                    for i in quizes:
                        passes += i.passed
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"{vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}, ты создал {len(quizes)} {com.make_agree_with_number(len(quizes)).word}.",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Твои опросы прошли {passes} раз.",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"{vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}, Вы не зарегистрированы на сайте. Зарегистрируйте его по этой ссылке: https://iquiz993zxc.glitch.me",
                                     random_id=random.randint(0, 2 ** 64))
            else:  # если пользователь написал нераспознанный текст
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"{vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}, я вас не понимаю. Вы можете узнать информацию об акааунте, написав 'инфо'",
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    bot()
