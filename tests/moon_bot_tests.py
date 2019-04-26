#!/usr/bin/python3

import unittest
import json
from moon_bot import *
from configuration import *

class TestMoonBot(unittest.TestCase):
    def setUp(self):
        config = Configuration("./tests/test_conf.json")
        self.moonBot = boockingBot(config)

    def test_init_type_buttons_from_conf(self):
        self.assertEqual(SERVICE_TYPES, ['Adding', 'Updating', 'Removing'])
        self.assertEqual(KEYBOARD_SERVICE_TYPE, {'one_time': True, 'buttons': [[
            {'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Adding'}, 'color': 'primary'},
            {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Updating'}, 'color': 'primary'},
            {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'Removing'}, 'color': 'primary'}]]})

    def test_init_services_buttons_from_conf(self):
        self.assertEqual(KEYBOARDS_SERVICES_BY_TYPE,
            {'Adding': {'one_time': True, 'buttons': [[
                {'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'a_one'}, 'color': 'primary'},
                {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'a_two'}, 'color': 'primary'},
                {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'a_three'}, 'color': 'primary'}]]},
             'Updating': {'one_time': True, 'buttons': [[
                 {'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'u_one'}, 'color': 'primary'},
                 {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'u_two'}, 'color': 'primary'},
                 {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'u_three'}, 'color': 'primary'}]]},
             'Removing': {'one_time': True, 'buttons': [[
                 {'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'r_one'}, 'color': 'primary'},
                 {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'r_two'}, 'color': 'primary'}]]}})


class TestUserAnswers(unittest.TestCase):
    def setUp(self):
        config = Configuration("./tests/test_conf.json")
        self.moonBot = boockingBot(config)
        self.moonBot.clients_table[1] = User(1, 'test_user')
        self.moonBot.clients_table[2] = User(2, 'sec_user', gift=True)

    def test_usual_greetings(self):
        self.assertEqual(self.moonBot.make_greetings(3, 'test_user_3')['message'],
                         "test_user_3, здравствуйте.\nНапишите, пожалуйста, ваш номер телефона.")

    def test_gifted_greetings(self):
        self.moonBot.config.make_gifts = True
        self.assertEqual(self.moonBot.make_greetings(3, 'test_user_3')['message'],
                         "test_user_3, здравствуйте.\nВаш подарочный сертификат ниже 🎁\nНапишите, пожалуйста, ваш номер телефона, чтобы мы могли забронировать за вами купон 😉")

    def test_answer_booking_needed(self):
        test_user = self.moonBot.clients_table[1]

        self.assertEqual(self.moonBot.receive_booking_needed(test_user, 'Привет')['message'],
                         "Может быть в следующий раз =)")

        self.assertEqual(self.moonBot.receive_booking_needed(test_user, 'Да')['message'],
                        "test_user, какой вид услуги вас интересует?\nНажмите кнопку или напишите сообщением один из вариантов. Так же вы можете написать сразу нужную услугу :)")

    def test_answer_another_service(self):
        test_user = self.moonBot.clients_table[1]

        self.assertEqual(self.moonBot.receive_add_more(test_user, 'Нет')['message'],
                         "В какой день вам удобно придти? Напишите это в диалог и мы вас запишем.")

        self.assertEqual(self.moonBot.receive_booking_needed(test_user, 'Да')['message'],
                        "test_user, какой вид услуги вас интересует?\nНажмите кнопку или напишите сообщением один из вариантов. Так же вы можете написать сразу нужную услугу :)")

    def test_add_service(self):
        test_user = self.moonBot.clients_table[1]

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.assertEqual(self.moonBot.receive_service_type(test_user, 'a_one')['message'],
                         'Спасибо) Хотите добавить еще услугу?\n')
        self.moonBot.receive_add_more(test_user, 'Нет')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:20'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:20:00 на процедуре a_one! ❤\n'})

    def test_time_collapse_checking(self):
        test_user = self.moonBot.clients_table[1]
        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.assertEqual(self.moonBot.receive_service_type(test_user, 'a_one')['message'],
                         'Спасибо) Хотите добавить еще услугу?\n')
        self.moonBot.receive_add_more(test_user, 'Нет')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:20'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:20:00 на процедуре a_one! ❤\n'})

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'u_two')
        self.moonBot.receive_add_more(test_user, 'Нет')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:36:00'})
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:36'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:36:00 на процедуре u_two! ❤\n'})

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'r_one')
        self.moonBot.receive_add_more(test_user, 'Нет')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:04:00'})

    def test_agrigate_few_services(self):
        test_user = self.moonBot.clients_table[1]

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.assertEqual(self.moonBot.receive_service_type(test_user, 'a_one')['message'],
                         'Спасибо) Хотите добавить еще услугу?\n')
        self.moonBot.receive_add_more(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'u_one')
        self.moonBot.receive_add_more(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'r_one')
        self.moonBot.receive_add_more(test_user, 'Нет')

        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:21:00 на процедурах a_one, u_one и r_one! ❤\n'})

    def test_add_or_not_gift(self):
        self.assertEqual(self.moonBot.send_greetings(self.moonBot.clients_table[1])['message'],
                         'test_user, здравствуйте.\nНапишите, пожалуйста, ваш номер телефона.')
        self.assertEqual(self.moonBot.send_greetings(self.moonBot.clients_table[2])['message'],
                         'sec_user, здравствуйте.\nВаш подарочный сертификат ниже \U0001F381\nНапишите, пожалуйста, ваш номер телефона, чтобы мы могли забронировать за вами купон \U0001F609')

class TestMobileNumberChecks(unittest.TestCase):
    def setUp(self):
        pass

    def test_letters_noly(self):
        self.assertEqual(False, is_mobile_number('rrasastrt'))

    def test_normal_number(self):
        self.assertEqual(True, is_mobile_number('+79134448855'))

    def test_normal_number_other_start(self):
        self.assertEqual(True, is_mobile_number('89134448855'))

    def test_one_letter_in(self):
        self.assertEqual(False, is_mobile_number('+791344488q5'))

    def test_one_letter_in_other_start(self):
        self.assertEqual(False, is_mobile_number('891344488q5'))

    def test_too_many(self):
        self.assertEqual(False, is_mobile_number('+791344488555'))

if __name__ == '__main__':
    unittest.main()