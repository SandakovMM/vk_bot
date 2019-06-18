import json
import os

class Configuration:
    def __init__(self, filename):
        configuration = None
        try:
            with open(filename) as configuration_file:
                configuration = json.load(configuration_file)
        except:
            print('Configuration file {} does not exist. Create it!'.format(filename))
            exit(0)

        try:
            self.api_vk_secret     = configuration['api_secret']
            self.confirm_vk_secret = configuration['confirm_secret']
            self.bot_module        = configuration['bot_module']
            self.make_gifts        = configuration['make_gifts']

            self.service_set       = configuration['service_set']
        except:
            print('Configuration file {} does not store needed parameters.'.format(filename))
            exit(0)

        try:
            # Use system env here to support fine configuration over docker compose
            self.db_url  = os.environ['DBHOST']
            self.db_port = os.environ['DBPORT']
        except:
            print('Enviroment don\'t has DBHOST or DBPORT varables, add it to show where is database.')
            exit(0)

    def get_confirm_secret(self):
        return self.confirm_vk_secret

    def get_api_secret(self):
        return self.api_vk_secret

    def get_service_set(self):
        return self.service_set

    def get_db_params(self):
        return (self.db_url, self.db_port)