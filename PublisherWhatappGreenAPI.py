import json
from PickleSerializer import PickleSerializer
import requests
from Processor import *


class PublisherWhatsappGreenApi(Processor):
    def __init__(self, args, processor):
        super().__init__(processor)
        self.chatId = None
        self.apiTokenInstance = None
        self.idInstance = None
        self.host = 'api.green-api.com'
        self.args = args
        self.authenticated = self.auth()
        if not self.authenticated:
            print('Error Authenticating to Green api, publisher will be skipped')

    def auth(self):
        auth_pickle = PickleSerializer('PublisherWhatsappGreenApi')
        if auth_pickle.exists():
            auth_data = auth_pickle.load()
            self.apiTokenInstance = auth_data['apiTokenInstance']
            self.idInstance = auth_data['idInstance']
            self.chatId = auth_data['chatId']
        else:
            print("*** Green API Auth ***")
            self.idInstance = input("Enter Instance Id: ")
            self.apiTokenInstance = input("Enter Api Token Instance: ")
            self.chatId = input("Enter ChatId/GroupId (Empty to create Group)")

            auth_pickle.create({
                'idInstance': self.idInstance,
                'apiTokenInstance': self.apiTokenInstance,
                'chatId': self.chatId
            })

        url = f'https://{self.host}/waInstance{self.idInstance}/getStateInstance/{self.apiTokenInstance}'
        response = requests.get(url)
        return response.status_code == 200 and json.loads(response.text)['stateInstance'] == 'authorized'

    def process_impl(self, filename):
        if not self.authenticated:
            return False
        if self.args.disablegreenapi:
            print("Green API is disabled, publish will be skipped.")
            return
        url = f'https://{self.host}/waInstance{self.idInstance}/sendFileByUpload/{self.apiTokenInstance}'
        payload = {'chatId': self.chatId, 'caption': '10Bot Coupon'}
        files = {'file': open(filename, 'rb')}
        response = requests.post(url, data=payload, files=files)
        if self.args.verbose:
            print(response.status_code)
            print(response.text)

