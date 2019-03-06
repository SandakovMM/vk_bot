#!/usr/bin/python3
from flask import Flask, request
from moon_bot import moonBot
import json

application_bot = moonBot()

app = Flask(__name__)

@app.route('/', methods=['POST'])
def processing():
    return application_bot.process_callback(json.loads(request.data))

if __name__ == '__main__':
    app.run(host='0.0.0.0')