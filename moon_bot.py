from enum import Enum
import copy

import json

from datetime import datetime, timedelta
from user import User, States

SERVICE_TYPES = [ 'Сахарная депиляция', 'Брови', 'Ресницы']

SERVICE_SET = {
    'Сахарная депиляция': [
        { 'name' : 'Глубокое бикини',
          'price':  600 },
        { 'name' : 'Классическое бикини',
          'price':  450 },
        { 'name' : 'Голень с коленом/бедра',
          'price':  550 },
        { 'name' : 'Ноги полностью',
          'price': 1000 },
        { 'name' : 'Любая зона на лице',
          'price':  200 },
        { 'name' : 'Спина/живот(полностью)',
          'price':  600 },
        { 'name' : 'Руки до локтя',
          'price':  450 },
        { 'name' : 'Руки полностью',
          'price':  600 },
        { 'name' : 'Подмышки',
          'price':  200 },

        { 'name'   : 'Комбо 1',
          'price'  :  900,
          'details': 'Глубокое бикини + голень (с коленом)'},
        { 'name'   : 'Комбо 2',
          'price'  : 1100,
          'details': 'глубокое бикини + голень (с коленом) + подмышечные впадины' },
        { 'name'   : 'Комбо 3',
          'price'  : 1300,
          'details': 'глубокое бикини + голень (с коленом) + подмышечные впадины' },
        { 'name'   : 'Комбо 4',
          'price'  : 1500,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины'},
        { 'name'   : 'Комбо 5',
          'price'  : 2000,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины + ручки полностью + зона над губой' },
    ],
    'Брови': [
        { 'name' : 'Оформление бровей + окрашивание краской',
          'price': 400 },
        { 'name' : 'Оформление бровей + окрашивание хной',
          'price': 600 },
        { 'name' : 'Долговременная укладка бровей',
          'price':  550,
          'details': 'глубокое бикини + ножки полностью + подмышечные впадины + ручки полностью + зона над губой' },
    ],
    'Ресницы': [
        { 'name' : 'Реконструкция ресниц Velve',
          'price': 1500 },
        { 'name' : 'Реконструкция ресниц Velvet + BOTOX 3D',
          'price': 1700 },
    ],
}


KEYBOARD_SERVICE_TYPE = {
    'one_time': True,
    'buttons': []
}

KEYBOARDS_SERVICES_BY_TYPE = { }

KEYBOARD_SERVICES = {
    'one_time': True,
    'buttons': []
}

def fill_buttons_from_data(buttons, data, data_extract_fn):
    array_pos = 1
    store_array = []

    for element in data:
        store_array.append(
            {'action': {
                'type': 'text',
                'payload': json.dumps({'buttons': array_pos}),
                'label': data_extract_fn(element),
            },
            'color': 'primary'})

        array_pos += 1

        if 0 == array_pos % 5:
            buttons['buttons'].append(store_array)
            store_array = []
            array_pos = 1

    buttons['buttons'].append(store_array)

def create_buttons():
    fill_buttons_from_data(KEYBOARD_SERVICE_TYPE, SERVICE_TYPES,
                           lambda data_element: data_element)

    for service_type in SERVICE_TYPES:
        type_keyboard = copy.deepcopy(KEYBOARD_SERVICES)
        fill_buttons_from_data(type_keyboard, SERVICE_SET[service_type],
                           lambda data_element: data_element['name'])
        KEYBOARDS_SERVICES_BY_TYPE[service_type] = type_keyboard

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

def extract_service_type(string):
    for service_type in SERVICE_TYPES:
        if string == service_type:
            return service_type
    return None

def is_valid_service(string):
    for _, services_by_type in SERVICE_SET.items():
        for service in services_by_type:
            if string == service['name']:
                return True
    return False

def parce_time(string):
    return datetime.strptime(string, '%d.%m.%Y %H:%M')

def is_time_free(string):
    return True

class Booking:
    def __init__(self, for_user):
        self.services = []
        self.time     = None
        self.user     = for_user

class BookingStore:
    def __init__(self):
        self.booking_list = []

    def check_time_free(self, time):
        for booking in self.booking_list:
            end_time = booking.time + timedelta(minutes = 15)
            if time >= booking.time and time <= end_time:
                return False

            new_procedure_end_time = time + timedelta(minutes = 15)
            if booking.time >= time and booking.time <= new_procedure_end_time:
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

    def add_bookig(self, to_add):
        self.booking_list.append(to_add)

class boockingBot:
    def __init__(self, configuration):
        self.booking_store   = BookingStore()
        self.clients_table   = {}
        self.prepare_booking = {} # store prepare booking by user_id

        self.config = configuration

    def send_greetings(self, user):
        user.state = States.ASK_FOR_NUMBER

        addition_msg_one = ''
        addition_msg_two = '.'
        if user.is_gifted():
            addition_msg_one = 'Ваш подарочный сертификат ниже \U0001F381\n'
            addition_msg_two = ', чтобы мы могли забронировать за вами купон \U0001F609'

        message_to_send = '{}, здравствуйте.\n{}Напишите, пожалуйста, ваш номер телефона{}'.format(user.first_name,
                           addition_msg_one, addition_msg_two)

        answer = { 'message': message_to_send }
        if user.is_gifted():
            answer['attachment'] = 'photo-126180933_456239557'
        return answer

    def make_greetings(self, user_id, user_name):
        user = self.clients_table.get(user_id)
        if None != user:
            # self.make_greetings(user) # <-- remove it later
            return # Already known user - don't do anything

        user = User(user_id, user_name, self.config.make_gifts)
        self.clients_table[user_id] = user
        return self.send_greetings(user)

    def send_is_booking_needed(self, user):
        user.state = States.ASK_FOR_NEED_BOOKING
        return { 'message': 'Хотите забронировать какую-то процедуру?',
                 'keyboard' : str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)) }

    def receive_number(self, user, message):

        if not is_mobile_number(message):
            return { 'message': 'Похоже это не номер мобильного, попробуйте другой. Пример номера: +78887776655' }

        user.phone = message

        answer = self.send_is_booking_needed(user)
        answer['message'] = 'Записали!\n' + answer['message']
        return answer

    def receive_booking_needed(self, user, message):
        if 'Да' == message:
            user.state = States.ASK_FOR_SERVICE_TYPE

            self.prepare_booking[user.user_id] = Booking(user)

            message_to_send = '{}, какой вид услуги вас интересует?\n'.format(user.first_name)
            message_to_send += 'Нажмите кнопку или напишите сообщением один из вариантов. Так же вы можете написать сразу нужную услугу :)'

            return { 'message': message_to_send,
                     'keyboard' : str(json.dumps(KEYBOARD_SERVICE_TYPE, ensure_ascii=False)) }

        user.state = States.KNOWN
        return { 'message': 'Может быть в следующий раз =)' }

    def receive_service_type(self, user, message):

        service_type = extract_service_type(message)
        if None == service_type:
            return self.receive_service(user, message)

        user.state = States.ASK_FOR_SERVICE

        message_to_send = 'Хорошо, выберите пожалуйста одину из услуг\n'
        return { 'message': message_to_send,
                 'keyboard' : str(json.dumps(KEYBOARDS_SERVICES_BY_TYPE[service_type],
                                  ensure_ascii=False)) }

    def receive_service(self, user, message):

        if not is_valid_service(message):
            return { 'message': 'Пожалуйста, выбирите один из предложеных вариантов' }

        self.prepare_booking[user.user_id].services.append(message)
        user.state = States.ASK_FOR_ANOTHER_SERV

        message_to_send  = 'Спасибо) Хотите добавить еще услугу?\n'
        return { 'message': message_to_send,
                 'keyboard' : str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)) }

    def receive_add_more(self, user, message):
        if 'Да' == message:
            user.state = States.ASK_FOR_SERVICE_TYPE

            message_to_send  = '{}, какая услуга вас интересует?\n'.format(user.first_name)
            message_to_send += 'Нажмите кнопку или напишите сообщением один из вариантов.'
            return { 'message': message_to_send,
                     'keyboard' : str(json.dumps(KEYBOARD_SERVICE_TYPE, ensure_ascii=False)) }

        user.state = States.ASK_FOR_DAY
        message_to_send = 'В какой день вам удобно придти? Напишите это в диалог и мы вас запишем.'
        return { 'message': message_to_send }

    def receive_service_day(self, user, message):
        try:
            geted_time = parce_time(message)
        except ValueError:
            return { 'message': 'Не совсем поняли вас. Пример даты и времени: 17.11.2018 12:00' }

        if not self.booking_store.check_time_free(geted_time):
            free_time = self.booking_store.find_close_free_time(geted_time)
            message_to_send = 'К сожалению данное время уже занято =('
            if None != free_time:
                message_to_send += ' Ближайшее свободное время {}'.format(free_time)

            return { 'message': message_to_send }

        prepared_booking = self.prepare_booking[user.user_id]
        prepared_booking.time = geted_time
        self.booking_store.add_bookig(prepared_booking)

        message_to_send  = 'Все готово, ура!\n'

        services_length = len(prepared_booking.services)
        prov_string = 'процедуре'
        if services_length != 1:
            prov_string = 'процедурах'

        message_to_send += 'Ждем вас {} на {}'.format(prepared_booking.time,
                                                      prov_string)

        counter = 1
        for booking_service in prepared_booking.services:
            if counter + 1 == services_length:
                message_to_send += ' {} и'.format(booking_service)
            elif counter == services_length:
                message_to_send += ' {}! \U00002764\n'.format(booking_service)
            else:
                message_to_send += ' {},'.format(booking_service)

            counter += 1

        user.state = States.KNOWN

        self.prepare_booking[user.user_id] = None # And delete it

        return { 'message': message_to_send }

    def create_answer_message(self, user, message):
        if States.INITIAL == user.state:
            return self.send_greetings(user)
        elif States.ASK_FOR_NUMBER == user.state:
            return self.receive_number(user, message)
        elif States.ASK_FOR_SERVICE_TYPE == user.state:
            return self.receive_service_type(user, message)
        elif States.ASK_FOR_SERVICE == user.state:
            return self.receive_service(user, message)
        elif States.ASK_FOR_ANOTHER_SERV == user.state:
            return self.receive_add_more(user, message)
        elif States.ASK_FOR_DAY == user.state:
            return self.receive_service_day(user, message)
        elif States.ASK_FOR_NEED_BOOKING == user.state:
            return self.receive_booking_needed(user, message)
        else:
            return self.send_is_booking_needed(user)

        return { 'message': 'Привет!' }

    def make_answer(self, user_id, message, user_name = None):
        user = self.clients_table.get(user_id)
        if None == user:
            if user_name == None:
                return None
            user = User(user_id, user_name, self.config.make_gifts)
            self.clients_table[user_id] = user

        return self.create_answer_message(user, message)

# if __name__ == "__main__":
#     bot = moonBot()

#     longpoll = VkLongPoll(bot.vk_session)

#     for event in longpoll.listen():
#         bot.process_event(event)