from enum import Enum
import json
import requests
from time import sleep
from datetime import datetime, timedelta

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from configuration import Configuration

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
    ASK_FOR_REPEAD  = 6

KEYBOARD_STEP_1 = {
    'one_time': True,
    'buttons': []
}

def create_buttons():
    array_pos = 1
    store_array = []

    for service in SERVICE_SET['services']:
        store_array.append(
            {'action': {
                'type': 'text',
                'payload': json.dumps({'buttons': array_pos}),
                'label': service['type'],
            },
            'color': 'primary'})

        array_pos += 1

        if 0 == array_pos % 5:
            KEYBOARD_STEP_1['buttons'].append(store_array)
            store_array = []
            array_pos = 1

        # print("Услуга {} с ценой {}".format(service['type'], service['price']))

    KEYBOARD_STEP_1['buttons'].append(store_array) # Last step

create_buttons()

YES_NO_KEYBORD = {
    'one_time': True,
    'buttons': [[
        {'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': 1}),
            'label': 'Да',
        },
        'color': 'positive'},

        {'action': {
            'type': 'text',
            'payload': json.dumps({'buttons': 2}),
            'label': 'Нет',
        },
        'color': 'negative'}
    ]]
}

# def test_is_mobile_number():
#     print(is_mobile_number('rrasastrt'))
#     print(is_mobile_number('+79137678498'))
#     print(is_mobile_number('89137678498'))
#     print(is_mobile_number('891376784q8'))
#     print(is_mobile_number('+791376784q8'))
#     print(is_mobile_number('+7913767849844'))

def is_mobile_number(string):
    length = len(string)
    if 12 != length and 11 != length:
        return False

    check_string = ''
    if 12 == length:
        if '+' != string[0]:
            return False
        check_string = string[1:]
    else:
        check_string = string

    if check_string.isdigit():
        return True
    return False

def is_valid_service(string):
    for service in SERVICE_SET['services']:
        if string == service['type']:
            return True
    return False

# def test_parce_time():
#     print(parce_time('11.12.2019 11:20'))

def parce_time(string):
    return datetime.strptime(string, '%d.%m.%Y %H:%M')

def is_time_free(string):
    return True

class Booking:
    def __init__(self):
        self.type = None
        self.time = None

class User:
    def __init__(self, user_id, user_profile, parant_bot):
        self.user_id = user_id
        self.first_name = user_profile[0]['first_name']
        self.phone      = None
        self.state      = States.INITIAL

        self.ready_bookings  = []
        self.prepare_booking = None

        self.parant_bot = parant_bot

    def send_greetings(self):
        self.state = States.ASK_FOR_NUMBER

        message_to_send  = '{}, здравствуйте.\n'.format(self.first_name)
        message_to_send += 'Ваш подарочный сертификат ниже \U0001F381\n'
        message_to_send += 'Напишите, пожалуйста, ваш номер телефона, чтобы мы могли забронировать за вами купон \U0001F609'
        return { 'message': message_to_send,
                 'attachment' : 'photo-126180933_456239557' }

    def receive_number(self, message):

        if not is_mobile_number(message):
            return { 'message': 'Похоже это не номер мобильного, попробуйте другой. Пример номера: +78887776655' }

        self.phone = message
        self.state = States.ASK_FOR_SERVICE

        message_to_send  = 'Записали!\n'
        message_to_send += '{}, какая услуга вас интересует?\n'.format(self.first_name)
        message_to_send += 'Нажмите кнопку или напишите сообщением один из вариантов.'
        return { 'message': message_to_send,
                 'keyboard' : str(json.dumps(KEYBOARD_STEP_1, ensure_ascii=False)) }

    def receive_service_type(self, message):

        if not is_valid_service(message):
            return { 'message': 'Пожалуйста, выбирите один из предложеных вариантов' }

        self.prepare_booking = Booking()
        self.prepare_booking.type = message
        self.state = States.ASK_FOR_DAY

        message_to_send  = 'Спасибо)\n'
        message_to_send  += 'В какой день вам удобно придти? Напишите это в диалог и мы вас запишем.'
        return { 'message': message_to_send }

    def receive_service_day(self, message):
        try:
            geted_time = parce_time(message)
        except ValueError:
            return { 'message': 'Не совсем поняли вас. Пример даты и времени: 17.11.2018 12:00' }

        if not self.parant_bot.check_time_free(geted_time):
            free_time = self.parant_bot.find_close_free_time(geted_time)
            message_to_send = 'К сожалению данное время уже занято =('
            if None != free_time:
                message_to_send += ' Ближайшее свободное время {}'.format(free_time)

            return { 'message': message_to_send }

        self.prepare_booking.time = geted_time
        self.ready_bookings.append(self.prepare_booking)

        message_to_send  = 'Все готово, ура!\n'
        message_to_send += 'Ждем вас {} на процедуре {}! \U00002764\n'.format(self.prepare_booking.time,
                                                                              self.prepare_booking.type)
        self.state = States.KNOWN

        return { 'message': message_to_send }

    def send_old_friend(self):
        self.state = States.ASK_FOR_REPEAD
        return { 'message': 'Привет! Хочешь забронировать какую-то процедуру?',
                 'keyboard' : str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)) }

    def receive_repead(self, message):
        if 'Да' == message:
            self.state = States.ASK_FOR_SERVICE

            message_to_send  = '{}, какая услуга вас интересует?\n'.format(self.first_name)
            message_to_send += 'Нажмите кнопку или напишите сообщением один из вариантов.'
            return { 'message': message_to_send,
                     'keyboard' : str(json.dumps(KEYBOARD_STEP_1, ensure_ascii=False)) }

        self.state = States.KNOWN
        return { 'message': 'Может быть в следующий раз =)' }

    def create_answer_message(self, message):
        if States.INITIAL == self.state:
            return self.send_greetings()
        elif States.ASK_FOR_NUMBER == self.state:
            return self.receive_number(message)
        elif States.ASK_FOR_SERVICE == self.state:
            return self.receive_service_type(message)
        elif States.ASK_FOR_DAY == self.state:
            return self.receive_service_day(message)
        elif States.ASK_FOR_REPEAD == self.state:
            return self.receive_repead(message)
        else:
            return self.send_old_friend()

        return { 'message': 'Привет!' }

    def use_this_time(self, time):
        for booking in self.ready_bookings:
            end_time = booking.time + timedelta(minutes = 15)
            if time >= booking.time and time <= end_time:
                return True

            new_procedure_end_time = time + timedelta(minutes = 15)
            if booking.time >= time and booking.time <= new_procedure_end_time:
                return True
        return False

class moonBot:
    def __init__(self):
        self.clients_table = {}
        self.config = Configuration('conf.json')

        self.vk_session = vk_api.VkApi(token=self.config.get_api_secret())
        self.vk = self.vk_session.get_api()

    def check_time_free(self, time):
        for _, client in self.clients_table.items():
            if client.use_this_time(time):
                return False
        return True

    def find_close_free_time(self, time):
        next_time = prev_time = time
        for _ in range(1, 60):
            next_time = next_time + timedelta(minutes = 1)
            if self.check_time_free(next_time):
                return next_time

            prev_time = prev_time - timedelta(minutes = 1)
            if self.check_time_free(prev_time):
                return prev_time

        return None

    def make_greetings(self, user):
        answer = user.send_greetings()
        try:
            self.vk.messages.send(user_id = user.user_id, random_id = get_random_id(),
                                  message    = answer.get('message'),
                                  attachment = answer.get('attachment'),
                                  keyboard   = answer.get('keyboard'))
        except vk_api.exceptions.ApiError as err:
            print(err)
            self.vk.messages.send(user_id = user.user_id, random_id = get_random_id(),
                                  message = user.first_name + ', чет не смогла, попробуй еще раз!')

    def make_answer(self, user, message):
        answer = user.create_answer_message(message)

        try:
            self.vk.messages.send(user_id = user.user_id, random_id = get_random_id(),
                                  message    = answer.get('message'),
                                  attachment = answer.get('attachment'),
                                  keyboard   = answer.get('keyboard'))
        except vk_api.exceptions.ApiError as err:
            print(err)
            self.vk.messages.send(user_id = user.user_id, random_id = get_random_id(),
                                  message = user.first_name + ', чет не смогла, попробуй еще раз!')


    def process_join(self, user_id):
        user = self.clients_table.get(user_id)
        if None != user:
            self.make_greetings(user) # <-- remove it later
            return # Already known user - don't do anything

        user_profile = self.vk.users.get(user_id = user_id)
        user = User(user_id, user_profile, self)
        self.clients_table[user_id] = user
        self.make_greetings(user)

    def process_message(self, user_id, message):
        user = self.clients_table.get(user_id)
        if None == user:
            user_profile = self.vk.users.get(user_id = user_id)
            user = User(user_id, user_profile, self)
            self.clients_table[user_id] = user

        self.make_answer(user, message)

    def process_event(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            self.process_message(event.user_id, event.text)

    def process_callback(self, request_json):
        print(request_json) # This is debug to known whats happend
        if 'type' not in request_json.keys():
            return 'not vk'
        if request_json['type'] == 'confirmation':
            return self.config.get_confirm_secret()
        elif request_json['type'] == 'group_join':
            self.process_join(request_json['object']['user_id'])
        elif request_json['type'] == 'message_new':
            self.process_message(request_json['object']['from_id'],
                                 request_json['object']['text'])
        return 'ok'

if __name__ == "__main__":
    bot = moonBot()

    longpoll = VkLongPoll(bot.vk_session)

    for event in longpoll.listen():
        bot.process_event(event)