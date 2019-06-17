#!/usr/bin/python3
from flask import Flask, request

# Standart
import json
from datetime import datetime, timedelta

# Libs
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

# Our modules
from configuration import Configuration
from moon_bot import boockingBot, DBConnectedBoockingBot

class vkMassageReceiver:
    def __init__(self, bot_type):
        # self.clients_table = {}
        self.config = Configuration('conf.json')

        self.vk_session = vk_api.VkApi(token=self.config.get_api_secret())
        self.vk = self.vk_session.get_api()
        self.bot_instance = bot_type(self.config)

    def process_join(self, user_id):
        user_profile = self.vk.users.get(user_id = user_id)
        user_name = user_profile[0]['first_name']
        return self.bot_instance.make_greetings(user_id, user_name)

    def process_message(self, user_id, message):
        return self.bot_instance.make_answer(user_id, message)

    def process_event(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            self.process_message(event.user_id, event.text)

    def process_callback(self, request_json):
        print(request_json) # This is debug to known whats happend
        answer = None
        user_id = None

        if 'type' not in request_json.keys():
            return 'not vk'
        if request_json['type'] == 'confirmation':
            return self.config.get_confirm_secret()
        elif request_json['type'] == 'group_join':
            user_id = request_json['object']['user_id']
            answer = self.process_join(user_id)
        elif request_json['type'] == 'message_new':
            user_id = request_json['object']['from_id']
            answer = self.process_message(user_id, request_json['object']['text'])
            if None == answer:
                answer = self.process_join(user_id)

        print("Send answer:")
        print(answer)

        if None == answer or None == user_id:
            return 'ok' # Not ok in real

        try:
            self.vk.messages.send(user_id = user_id, random_id = get_random_id(),
                                  message    = answer.get('message'),
                                  attachment = answer.get('attachment'),
                                  keyboard   = answer.get('keyboard'))
        except vk_api.exceptions.ApiError as err:
            print(err)
            self.vk.messages.send(user_id = user_id, random_id = get_random_id(),
                                  message = 'Извеняюсь, что то пошло не так. Обратитесь на прямую к адменистратору сообщества')


        return 'ok'

# application_bot = vkMassageReceiver(boockingBot)
application_bot = vkMassageReceiver(DBConnectedBoockingBot)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def processing():
    return application_bot.process_callback(json.loads(request.data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("80"))