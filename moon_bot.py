from enum import Enum

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

class States(Enum):
    INITIAL = 1
    KNOWN   = 2

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        user_profile = vk.users.get(user_id = self.user_id)

        self.first_name = user_profile[0]['first_name']
        self.state = States.INITIAL

    def send_greetings(self):
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = self.first_name + ', здравствуйте')

        vk.message.send(user_id    = self.user_id,
                        random_id  = get_random_id(),
                        message    = 'Лолируем',
                        attachment = 'photo-126180933_456239557')
        self.state = States.KNOWN

    def send_old_friend(self):
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = self.first_name + ', я тебя узнал! Деревянными членами торгуешь!')
        self.state = States.INITIAL

    def make_answer(self, event):
        try:
            if States.INITIAL == self.state:
                self.send_greetings()
            else:
                self.send_old_friend()
        except vk_api.exceptions.ApiError as err:
            print(err)
            vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = self.first_name + ', чет не смогла, попробуй еще раз!')

def process_message(event, clients_table):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        # Слушаем longpoll, если пришло сообщение то:
        user = clients_table.get(event.user_id)
        if None == user:
            user = User(event.user_id)
            clients_table[event.user_id] = user

        # if event.text == 'Первый вариант фразы' or event.text == 'Второй вариант фразы': #Если написали заданную фразу
        user.make_answer(event)

if __name__ == "__main__":
    clients_table = {}

    vk_session = vk_api.VkApi(token='48acd070c2f03c468317f6d855616f3017dee55f138cf3850bf37e6cf360d5f9d8a471bd8b7edf2e93a89')

    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    for event in longpoll.listen():
        process_message(event, clients_table)