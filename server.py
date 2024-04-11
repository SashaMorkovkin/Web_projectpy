from server import main
from vk_bot.vk_bot_api import bot
import threading


def start_site():
    serv = threading.Thread(target=main)
    vkbot = threading.Thread(target=bot, daemon=True)
    serv.start()
    vkbot.start()
    vkbot.join()


if __name__ == '__main__':
    start_site()
    print('Started')
