#!/usr/bin/python3

import unittest
import json
from moon_bot import *
from configuration import *

# class TestMoonBot(unittest.TestCase):
#     def setUp(self):
#         config = Configuration("conf.json")
#         self.moonBot = boockingBot(config)

    # def test_expect_vk(self):
    #     self.assertEqual(self.moonBot.process_callback({"nothing" : "nothing"}),
    #                      'not vk')

    # def test_init_buttons_from_conf(self):
    #     print(KEYBOARDS_SERVICES_BY_TYPE)

class TestUserAnswers(unittest.TestCase):
    def setUp(self):
        config = Configuration("conf.json")
        self.moonBot = boockingBot(config)
        self.moonBot.clients_table[1] = User(1, 'test_user')
        self.moonBot.clients_table[2] = User(2, 'sec_user', gift=True)

    def test_time_checking(self):
        test_user = self.moonBot.clients_table[1]
        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.assertEqual(self.moonBot.receive_service_type(test_user, 'Комбо 1')['message'],
                         'Спасибо) Хотите добавить еще услугу?\n')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:20'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:20:00 на процедуре Комбо 1! ❤\n'})

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'Комбо 2')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:36:00'})
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:36'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:36:00 на процедуре Комбо 2! ❤\n'})

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.moonBot.receive_service_type(test_user, 'Комбо 3')
        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:04:00'})

    def test_show_all_services(self):
        test_user = self.moonBot.clients_table[1]

        self.moonBot.receive_booking_needed(test_user, 'Да')
        self.assertEqual(self.moonBot.receive_service_type(test_user, 'Комбо 1')['message'],
                         'Спасибо) Хотите добавить еще услугу?\n')
        self.moonBot.receive_service_type(test_user, 'Комбо 2')
        self.moonBot.receive_service_type(test_user, 'Комбо 3')

        self.assertEqual(self.moonBot.receive_service_day(test_user, '11.12.2019 11:21'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:21:00 на процедурах Комбо 1, Комбо 2 и Комбо 3! ❤\n'})

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


# This tests not available for now
# class KeyboardCreateTest(unittest.TestCase):
#     def setUp(self):
#         pass

    # def test_yes_no_keyboard_format(self):
    #     print(str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)))

    # def test_service_keyboard_format(self):
    #     expect_result = {"one_time": True, "buttons": [[{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Брови"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Брови"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Брови"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Ресницы"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Ресницы"}, "color": "primary"}]]}
    #     self.assertEqual(expect_result, KEYBOARD_STEP_1)

    # def test_service_types_keyboard_format(self):
    #     expect_result = {"one_time": True,
    #         "buttons": [
    #             [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Create"}, "color": "primary"},
    #              {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Update"}, "color": "primary"},
    #              {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Delete"}, "color": "primary"}]]}
    #     services_description = [{ "service_type": "Create", "services": [ { "name": "one" },   { "name": "two"},    ] },
    #                             { "service_type": "Update", "services": [ { "name": "other" }, { "name": "make"},   ] },
    #                             { "service_type": "Delete", "services": [ { "name": "first" }, { "name": "second"}, ] } ]
    #     feel_service_store(services_description)
    #     create_buttons()
    #     self.assertEqual(expect_result, KEYBOARD_SERVICE_TYPE)

    # def test_service_keyboards_format(self):
    #     expect_result1 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'one'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'two'}, 'color': 'primary'}]]}
    #     expect_result2 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'other'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'make'}, 'color': 'primary'}]]}
    #     expect_result3 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'first'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'second'}, 'color': 'primary'}]]}

    #     services_description = [{ "service_type": "Create", "services": [ { "name": "one" },   { "name": "two"},    ] },
    #                             { "service_type": "Update", "services": [ { "name": "other" }, { "name": "make"},   ] },
    #                             { "service_type": "Delete", "services": [ { "name": "first" }, { "name": "second"}, ] } ]
    #     feel_service_store(services_description)
    #     create_buttons()

    #     self.assertEqual(expect_result1, KEYBOARDS_SERVICES_BY_TYPE['Create'])
    #     self.assertEqual(expect_result2, KEYBOARDS_SERVICES_BY_TYPE['Update'])
    #     self.assertEqual(expect_result3, KEYBOARDS_SERVICES_BY_TYPE['Delete'])

if __name__ == '__main__':
    unittest.main()