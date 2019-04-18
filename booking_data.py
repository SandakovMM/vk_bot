#!/usr/bin/python3

from enum import Enum
from datetime import datetime, timedelta
import json

from pymongo import MongoClient

class States(Enum):
    INITIAL              = 1
    ASK_FOR_NUMBER       = 2
    ASK_FOR_SERVICE      = 3
    ASK_FOR_DAY          = 4
    KNOWN                = 5
    ASK_FOR_NEED_BOOKING = 6
    ASK_FOR_SERVICE_TYPE = 7
    ASK_FOR_ANOTHER_SERV = 8

class Booking:
    def __init__(self, for_user):
        self.services = []
        self.time     = None
        self.user_id  = for_user

    def __repr__(self):
        return "Booking for user {} at {}. Services: {}.".format(self.user_id,
                str(self.time), self.services)

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
        if not self.check_time_free(to_add.time):
            return False

        self.booking_list.append(to_add)
        return True

class DBBookingStore(BookingStore):
    def __init__(self, db_path = ("localhost", 27017)):
        self.db_url, self.db_port = db_path

        super().__init__()

        connection = MongoClient(self.db_url, self.db_port)
        base = connection.booking_bot_base
        booking_collection = base.booking_collection

        for booking in booking_collection.find():
            need_to_add = Booking(booking["user_id"])
            # Use there standart time format
            need_to_add.time = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
            for service in booking["services"]:
                need_to_add.services.append(service)
            
            self.booking_list.append(need_to_add)

        connection.close()

    def add_bookig(self, to_add):
        if not super().add_bookig(to_add):
            return False

        connection = MongoClient(self.db_url, self.db_port)
        base = connection.booking_bot_base
        booking_collection = base.booking_collection

        booking_to_add = {"user_id": to_add.user_id, "time": str(to_add.time),
                          "services": to_add.services }
        booking_collection.insert_one(booking_to_add)

        connection.close()

        return True

class User:
    def __init__(self, user_id, user_name, phone = None,
                 state = States.INITIAL, gift = False):
        self._user_id    = user_id
        self._first_name = user_name
        # user_profile[0]['first_name']
        self._phone      = phone
        self._state      = state

        self.gift_geted = gift
        # Thats how we check that it's new user and we need some raection
        if None == phone and States.INITIAL == self._state:
            self.user_state_changed()

    def user_state_changed(self):
        pass

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state in [item for item in States]:
            self._state = state
            self.user_state_changed()

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, phone_number):
        self._phone = phone_number
        self.user_state_changed()

    @property
    def user_id(self):
        return self._user_id

    @property
    def first_name(self):
        return self._first_name

    def is_gifted(self):
        return self.gift_geted

    def __repr__(self):
        return "User {} on state {}. Phone {}.".format(self._first_name,
                self._state.name, self._phone)

class SavedToDBUser(User):
    def __init__(self, user_id, user_name, phone = None,
                 state = States.INITIAL, gift = False,
                 db_path = ("localhost", 27017)):
        self.db_url, self.db_port = db_path
        super().__init__(user_id, user_name, phone, state, gift)

    def user_state_changed(self):
        # Just open connection and send all we need
        connection = MongoClient(self.db_url, self.db_port)
        base = connection.booking_bot_base
        clients = base.clients_collection
        if None == clients.find_one({"id": self._user_id}):
            doc = {"id":     self._user_id, "name":  self._first_name,
                   "phone":  self._phone,   "state": self._state.name,
                   "gifted": self.gift_geted }
            clients.insert_one(doc)
            connection.close()
            return

        clients.update_one({"id": self._user_id},
                           {"$set": {"phone": self._phone,
                                     "state": self._state.name} } )
        connection.close()

    def __repr__(self):
        return super().__repr__()  " Saved to DataBase"

class DBUserExtracter():
    def __init__(self, db_path = ("localhost", 27017)):
        self.db_path = db_path
        db_url, db_port = db_path
        self.connection = MongoClient(db_url, db_port)
        self.base       = self.connection.booking_bot_base
        self.clients    = self.base.clients_collection

    def extract_users(self):
        result = { }
        for client in self.clients.find():
            # Need to avoid saeing here
            user = SavedToDBUser(client["id"], client["name"],
                                 phone = client["phone"],
                                 state = States[client["state"]],
                                 gift  = client["gifted"],
                                 db_path = self.db_path)

            # We don't remember prepare booking for now, so just drop this states on reboot
            if user.state in [States.ASK_FOR_SERVICE, States.ASK_FOR_DAY,
                              States.ASK_FOR_SERVICE_TYPE, States.ASK_FOR_ANOTHER_SERV]:
                user.state = States.KNOWN

            result[client["id"]] = user

        return result

    def __del__(self):
        self.connection.close()

# if __name__ == "__main__":
#     user = User(1, "aaa", None)
#     print(user.state)
#     user.state = States.ASK_FOR_NEED_BOOKING
#     print(user.state)