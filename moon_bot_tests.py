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


class KeyboardCreateTest(unittest.TestCase):
    def setUp(self):
        pass

    # def test_yes_no_keyboard_format(self):
    #     print(str(json.dumps(YES_NO_KEYBORD, ensure_ascii=False)))

    # def test_service_keyboard_format(self):
    #     expect_result = {"one_time": True, "buttons": [[{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Сахарная депиляция"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Брови"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 4}", "label": "Брови"}, "color": "primary"}], [{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Брови"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Ресницы"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Ресницы"}, "color": "primary"}]]}
    #     self.assertEqual(expect_result, KEYBOARD_STEP_1)

    def test_service_types_keyboard_format(self):
        expect_result = {"one_time": True, "buttons": [[{"action": {"type": "text", "payload": "{\"buttons\": 1}", "label": "Сахарная депиляция"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 2}", "label": "Брови"}, "color": "primary"}, {"action": {"type": "text", "payload": "{\"buttons\": 3}", "label": "Ресницы"}, "color": "primary"}]]}
        self.assertEqual(expect_result, KEYBOARD_SERVICE_TYPE)

    def test_service_keyboards_format(self):
        expect_result1 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Глубокое бикини'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Классическое бикини'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'Голень с коленом/бедра'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 4}', 'label': 'Ноги полностью'}, 'color': 'primary'}], [{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Любая зона на лице'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Спина/живот(полностью)'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'Руки до локтя'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 4}', 'label': 'Руки полностью'}, 'color': 'primary'}], [{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Подмышки'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Комбо 1'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'Комбо 2'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 4}', 'label': 'Комбо 3'}, 'color': 'primary'}], [{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Комбо 4'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Комбо 5'}, 'color': 'primary'}]]}
        expect_result2 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Оформление бровей + окрашивание краской'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Оформление бровей + окрашивание хной'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 3}', 'label': 'Долговременная укладка бровей'}, 'color': 'primary'}]]}
        expect_result3 = {'one_time': True, 'buttons': [[{'action': {'type': 'text', 'payload': '{"buttons": 1}', 'label': 'Реконструкция ресниц Velve'}, 'color': 'primary'}, {'action': {'type': 'text', 'payload': '{"buttons": 2}', 'label': 'Реконструкция ресниц Velvet + BOTOX 3D'}, 'color': 'primary'}]]}
        self.assertEqual(expect_result1,
                         KEYBOARDS_SERVICES_BY_TYPE['Сахарная депиляция'])
        self.assertEqual(expect_result2,
                         KEYBOARDS_SERVICES_BY_TYPE['Брови'])
        self.assertEqual(expect_result3,
                         KEYBOARDS_SERVICES_BY_TYPE['Ресницы'])

if __name__ == '__main__':
    unittest.main()