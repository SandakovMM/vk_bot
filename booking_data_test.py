#!/usr/bin/python3

import unittest
import json
from booking_data import *

# class TestUser(User):
#     __init__(self, user_id, user_name, gift = False):
#         super().__init__(user_id, user_name, gift)

#     def user_state_changed(self):
#         pass


# class TestUsers(unittest.TestCase):
#     def setUp(self):
#         pass

class TestBooking(unittest.TestCase):
    def setUp(self):
        pass

    def test_json_serialization(self):
        booking_instance = Booking(1)
        booking_instance.time = 10
        booking_instance.services.append("One")
        booking_instance.services.append("Two")

        print(json.dumps(booking_instance.__dict__))


class TestDBUsers(unittest.TestCase):
    def setUp(self):
        conn = MongoClient('127.0.0.1', 27017)
        db = conn.booking_bot_base
        db.clients_collection.drop()
        pass

    def test_save_user(self):
        user1 = SavedToDBUser(1, "user1", gift = True)
        user2 = SavedToDBUser(2, "user2", gift = False)

        user1.phone = "9999999"
        user2.state = States.ASK_FOR_SERVICE

    def test_get_users(self):
        user1 = SavedToDBUser(1, "user1", gift = True)
        user2 = SavedToDBUser(2, "user2", gift = False)

        user1.state = States.ASK_FOR_SERVICE
        user2.phone = "9997999"

        users_list = DBUserExtracter().extract_users()
        print("Geted list: {}".format(users_list))

if __name__ == '__main__':
    unittest.main()