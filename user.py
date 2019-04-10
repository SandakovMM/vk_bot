#!/usr/bin/python3

from enum import Enum

class States(Enum):
    INITIAL              = 1
    ASK_FOR_NUMBER       = 2
    ASK_FOR_SERVICE      = 3
    ASK_FOR_DAY          = 4
    KNOWN                = 5
    ASK_FOR_NEED_BOOKING = 6
    ASK_FOR_SERVICE_TYPE = 7
    ASK_FOR_ANOTHER_SERV = 8

class User:
    def __init__(self, user_id, user_name, gift = False):
        self._user_id    = user_id
        self._first_name = user_name
        # user_profile[0]['first_name']
        self._phone      = None
        self._state      = States.INITIAL

        self.gift_geted = gift

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state in [item for item in States]:
            self._state = state

    @property
    def phone(self):
        return self._state

    @phone.setter
    def phone(self, phone_number):
        self.phone = phone_number

    @property
    def user_id(self):
        return self._user_id

    @property
    def first_name(self):
        return self._first_name

    def is_gifted(self):
        return self.gift_geted

if __name__ == "__main__":
    user = User(1, "aaa", None)
    print(user.state)
    user.state = States.ASK_FOR_NEED_BOOKING
    print(user.state)