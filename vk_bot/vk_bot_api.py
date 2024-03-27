import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

TOKEN = 'vk1.a.iKxIo89g-nr1A5X_-fhiztJ7OCwMbuV2hugyx3t47_KDN5ZbNOe2NT8aw5dj5PHtqB9LbH2ZKMqcqLC8eWenqmPSVfkaaoE7pD87NdwWXISA8eEu0fWoQWnvA16rx9ABQy6qu22uR6ZKyz3NAJ-cOADRatWut_6MTrC9w9_Y6r02Oil5hEnW17S58U_x_TMmw8yVuI5pW7YCJt2RKJM6sQ'


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, '225254028')

    for event in longpoll.listen():
        print(event)
        vk = vk_session.get_api()
        if event.type == VkBotEventType.GROUP_JOIN and vk.users.get(user_id=event.object.user_id):
            vk.messages.send(user_id=event.object.user_id,
                             message=f"Привет, {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']}! Нет аккаунта? Зарегистрируйте его по этой ссылке: *ссылка*",
                             random_id=random.randint(0, 2 ** 64))
            print(
                f"пользователь {vk.users.get(user_id=event.object.user_id, fields='first_name')[0]['first_name']} присоединился!")

        if event.type == VkBotEventType.MESSAGE_NEW and vk.groups.isMember(group_id='225254028',
                                                                           user_id=event.obj.message['from_id']) == 0:
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=f"Привет, {vk.users.get(user_id=event.obj.message['from_id'], fields='first_name')[0]['first_name']}! Вот ссылка на авторизацию: *ссылка*",
                             random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
