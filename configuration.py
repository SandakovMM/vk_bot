import json

class Configuration:
    def __init__(self, filename):
        try:
            with open(filename) as configuration_file:
                configuration = json.load(configuration_file)

            self.api_vk_secret     = configuration['api_secret']
            self.confirm_vk_secret = configuration['confirm_secret']
            self.bot_module        = configuration['bot_module']
        except:
            print('Configuration file conf.json does not exist. Create it')
            exit(0)

    def get_confirm_secret(self):
        return self.confirm_vk_secret

    def get_api_secret(self):
        return self.api_vk_secret