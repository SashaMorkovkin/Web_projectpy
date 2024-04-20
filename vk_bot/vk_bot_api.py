import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.users import User
from data.quezes import Quezes

TOKEN = ('vk1.a.iKxIo89g-nr1A5X_-fhiztJ7OCwMbuV2hugyx3t47_KDN5ZbNOe2NT8aw5dj5PHtqB9LbH2ZKMqcqLC8eWe'
         'nqmPSVfkaaoE7pD87NdwWXISA8eEu0fWoQWnvA16rx9ABQy6qu22uR6ZKyz3NAJ-cOADRatWut_6MTrC9w9_Y6r02'
         'Oil5hEnW17S58U_x_TMmw8yVuI5pW7YCJt2RKJM6sQ')


def bot():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, '225254028')
    for event in longpoll.listen():
        vk = vk_session.get_api()
        if event.type == VkBotEventType.GROUP_JOIN and vk.users.get(user_id=event.object.user_id):
            vk.messages.send(user_id=event.object.user_id,
                             message=f"Привет, {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']}! Нет аккаунта? Зарегистрируйте его по этой ссылке: *ссылка*",
                             random_id=random.randint(0, 2 ** 64))
            print(
                f"пользователь {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']} присоединился!")
        if event.type == VkBotEventType.MESSAGE_NEW:
            member = vk.groups.isMember(group_id=225254028, user_id=event.obj.message['from_id'])
            if member == 0:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"Привет, {vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}! Для прохождения опросов нужно подписаться на бота👆",
                                 random_id=random.randint(0, 2 ** 64))
            else:
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.vk_id == event.obj.message['from_id']).first()
                print(user)
                quezes = db_sess.query(Quezes).filter(Quezes.authorid == user.id).all()
                print(quezes)