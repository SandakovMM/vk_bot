#!/usr/bin/python3

import unittest
import json
from moon_bot import *

class TestMoonBot(unittest.TestCase):
    def setUp(self):
        self.moonBot = moonBot()

    def test_expect_vk(self):
        self.assertEqual(self.moonBot.process_callback({"nothing" : "nothing"}),
                         'not vk')

class TestUserAnswers(unittest.TestCase):
    def setUp(self):
        self.moonBot = moonBot()
        self.moonBot.clients_table[1] = User(1, [{'first_name':'test_user'}], self.moonBot)

    def test_time_checking(self):
        test_user = self.moonBot.clients_table[1]
        self.assertEqual(test_user.receive_service_type('Комбо 1'),
                         {'message': 'Спасибо)\nВ какой день вам удобно придти? Напишите это в диалог и мы вас запишем.'})
        self.assertEqual(test_user.receive_service_day('11.12.2019 11:20'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:20:00 на процедуре Комбо 1! ❤\n'})

        test_user.receive_service_type('Комбо 2')
        self.assertEqual(test_user.receive_service_day('11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:36:00'})
        self.assertEqual(test_user.receive_service_day('11.12.2019 11:36'),
                         {'message': 'Все готово, ура!\nЖдем вас 2019-12-11 11:36:00 на процедуре Комбо 2! ❤\n'})

        test_user.receive_service_type('Комбо 3')
        self.assertEqual(test_user.receive_service_day('11.12.2019 11:21'),
                         {'message': 'К сожалению данное время уже занято =( Ближайшее свободное время 2019-12-11 11:04:00'})


# class KeyboardCreateTest(unittest.TestCase):
#     def setUp(self):
#         pass

    # def test_yes_no_keyboard_format(self):
    #     print(str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)))

    # def test_service_keyboard_format(self):
    #     print(str(json.dumps(KEYBOARD_STEP_1, ensure_ascii=False)))

if __name__ == '__main__':
    unittest.main()