from PickleSerializer import PickleSerializer
import requests
from ReportProcessor import *


class PublisherWhatsappGreenApi(ReportProcessor):
    def __init__(self, processor):
        super().__init__(processor)
        self.chatId = None
        self.apiTokenInstance = None
        self.idInstance = None
        self.host = 'api.green-api.com'
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
            self.idInstance = input("Enter api.green-api.com InstanceId: ")
            self.apiTokenInstance = input("Enter api.green-api.com Api Token")
            self.chatId = input("Enter chatId")
            auth_pickle.create({
                'idInstance': self.idInstance,
                'apiTokenInstance': self.apiTokenInstance,
                'chatId': self.chatId
            })

        # todo : check the validate of the auth, buy using some dummy api.
        return True

    def process_impl(self, filename):
        if not self.authenticated:
            return False
        url = f'https://{self.host}/waInstance{self.idInstance}/sendFileByUpload/{self.apiTokenInstance}'
        payload = {'chatId': self.chatId, 'caption': '10Bot Coupon'}
        files = {'file': open(filename, 'rb')}
        response = requests.post(url, data=payload, files=files)
        print(response.status_code)
        print(response.text)

