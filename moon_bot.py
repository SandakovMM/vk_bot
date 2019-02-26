from enum import Enum
import json
import requests
from time import sleep

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

SERVICE_SET = {
    'services': [
        { 'type': 'Глубокое бикини',        'price':  600 },
        { 'type': 'Классическое бикини',    'price':  450 },
        { 'type': 'Голень с коленом/бедра', 'price':  550 },
        { 'type': 'Ноги полностью',         'price': 1000 },
        { 'type': 'Любая зона на лице',     'price':  200 },
        { 'type': 'Спина/живот(полностью)', 'price':  600 },
        { 'type': 'Руки до локтя',          'price':  450 },
        { 'type': 'Руки полностью',         'price':  600 },
        { 'type': 'Подмышки',               'price':  200 },

        { 'type'   : 'Комбо 1',
          'price'  :  900,
          'details': 'Глубокое бикини + голень (с коленом)'},
        { 'type'   : 'Комбо 2',
          'price'  : 1100,
          'details': 'глубокое бикини + голень (с коленом) + подмышечные впадины' },
        { 'type'   : 'Комбо 3',
          'price'  : 1300,
          'details': 'глубокое бикини + голень (с коленом) + подмышечные впадины' },
        { 'type'   : 'Комбо 4',
          'price'  : 1500,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины'},
        { 'type'   : 'Комбо 5',
          'price'  : 2000,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины + ручки полностью + зона над губой' },

        { 'type': 'Оформление бровей + окрашивание краской', 'price': 400 },
        { 'type': 'Оформление бровей + окрашивание хной',    'price': 600 },
        { 'type': 'Долговременная укладка бровей',
          'price':  550,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины + ручки полностью + зона над губой' },

        { 'type': 'Реконструкция ресниц Velve',             'price': 1500 },
        { 'type': 'Реконструкция ресниц Velvet + BOTOX 3D', 'price': 1700 },
    ]
}

class States(Enum):
    INITIAL         = 1
    ASK_FOR_NUMBER  = 2
    ASK_FOR_SERVICE = 3
    ASK_FOR_DAY     = 4
    KNOWN           = 5

KEYBOARD_STEP_1 = {
    'one_time': False,
    'buttons': [[{
        'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': '1'}),
            'label': 'Предыдущая',
        },
        'color': 'negative'
    },
    {
        'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': '2'}),
            'label': 'Pred',
        },
        'color': 'primary'
    },
    {
        'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': '3'}),
            'label': 'aaa bbb',
        },
        'color': 'primary'
    },
    {
        'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': '4'}),
            'label': 'глубокое бикини + ножки полностью',
        },
        'color': 'primary'
    },
    ],[
    {
        'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': '5'}),
            'label': 'Здорова!',
        },
        'color': 'primary'
    }
    ]]
}

def is_mobile_number(string):
    return True

def is_valid_service(string):
    return True

def is_valid_time(string):
    return True

def is_time_free(string):
    return True

class Booking:
    def __init__(self):
        self.type = None
        self.time = None

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        user_profile = vk.users.get(user_id = self.user_id)

        self.first_name = user_profile[0]['first_name']
        self.phone      = None
        self.state      = States.INITIAL

        self.ready_bookings  = []
        self.prepare_booking = None

    def send_greetings(self):
        message_to_send  = '{}, здравствуйте.\n'.format(self.first_name)
        message_to_send += 'Ваш подарочный сертификат ниже \U0001F381\n'
        message_to_send += 'Напишите, пожалуйста, ваш номер телефона, чтобы мы могли забронировать за вами купон \U0001F609'
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = message_to_send,
                         attachment= 'photo-126180933_456239557')

        # Как это сделать?
        # sleep(0.1)
        # vk.message.send(user_id    = self.user_id,
        #                 random_id  = get_random_id(),
        #                 message    = 'Лолируем')
        # vk.message.send(user_id    = self.user_id,
        #                 random_id  = get_random_id(),
        #                 message    = 'https://disgustingmen.com/wp-content/uploads/2019/02/120-1024x586.jpg')
        self.state = States.ASK_FOR_NUMBER

    def receive_number(self, event):

        if not is_mobile_number(event.text):
            vk.messages.send(user_id   = self.user_id,
                             random_id = get_random_id(),
                             message   = 'Похоже это не номер мобильного, попробуйте другой. Пример номера: +78887776655')
            return

        self.phone = event.text

        message_to_send  = 'Записали!\n'
        message_to_send  += '{}, какая услуга вас интересует?\n'.format(self.first_name)
        message_to_send += 'Нажмите кнопку или напишите сообщением один из вариантов.'
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = message_to_send,
                         keyboard  = str(json.dumps(KEYBOARD_STEP_1, ensure_ascii=False)))

        self.state = States.ASK_FOR_SERVICE

    def receive_service_type(self, event):

        if not is_valid_service(event.text):
            vk.messages.send(user_id   = self.user_id,
                             random_id = get_random_id(),
                             message   = 'Пожалуйста, выбирите один из предложеных вариантов')
            return

        self.prepare_booking = Booking()
        self.prepare_booking.type = event.text

        message_to_send  = 'Спасибо)\n'
        message_to_send  += 'В какой день вам удобно придти? Напишите это в диалог и мы вас запишем.'
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = message_to_send)

        self.state = States.ASK_FOR_DAY

    def receive_service_day(self, event):

        if not is_valid_time(event.text):
            vk.messages.send(user_id   = self.user_id,
                             random_id = get_random_id(),
                             message   = 'Не совсем поняли вас. Пример даты и времени: 17.11.2018 в 12:00')
            return

        if not is_time_free(event.text):
            vk.messages.send(user_id   = self.user_id,
                             random_id = get_random_id(),
                             message   = 'К сожалению данное время уже занято, выбирите другое')
            return

        self.prepare_booking.time = event.text
        self.ready_bookings.append(self.prepare_booking)

        message_to_send  = 'Все готово, ура!\n'
        message_to_send += 'Ждем вас {} на процедуре {}! \U00002764\n'.format(self.prepare_booking.time,
                                                                             self.prepare_booking.type)
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = message_to_send)

        self.state = States.KNOWN

    def send_old_friend(self):
        vk.messages.send(user_id   = self.user_id,
                         random_id = get_random_id(),
                         message   = self.first_name + ', я тебя узнал!')
        self.state = States.INITIAL

    def make_answer(self, event):
        try:
            if States.INITIAL == self.state:
                self.send_greetings()
            elif States.ASK_FOR_NUMBER == self.state:
                self.receive_number(event)
            elif States.ASK_FOR_SERVICE == self.state:
                self.receive_service_type(event)
            elif States.ASK_FOR_DAY == self.state:
                self.receive_service_day(event)
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