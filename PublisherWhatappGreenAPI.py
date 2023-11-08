import json
from PickleSerializer import PickleSerializer
import requests
import re
from Processor import *


class PublisherWhatsappGreenApi(Processor):
    group_pattern = re.compile(r'^\d{18}@g\.us$')
    chatid_pattern = re.compile(r'^\d{13}@c\.us$')

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

    def create_group(self, chat_ids):
        url = f'https://{self.host}/waInstance{self.idInstance}/createGroup/{self.apiTokenInstance}'
        payload = { 'groupName': "10Bot", 'chatIds': chat_ids}
        headers = { 'Content-Type': 'application/json' }
        response = requests.post(url, headers=headers, data=json.dumps(payload, sort_keys=False))
        if response.status_code != 200:
            raise RuntimeError(f'Green API Error:{response.status_code} message:{response.text}')

        resp_json = json.loads(response.text)
        if not resp_json['created']:
            raise RuntimeError(f'Green API Error:{response.status_code} message:{response.text}')
        print(f"WhatsApp Group created Id={resp_json['chatId']}, invitelink={resp_json['groupInviteLink']}")
        return resp_json['chatId']

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
            self.chatId = input("Enter ChatId/GroupId (Empty to create Group): ")

            if self.chatId == '':
                chat_ids = []
                while True:
                    msisdn = input("Enter ChatId(Empty When Done): ")
                    if self.chatid_pattern.match(msisdn):
                        chat_ids.append(msisdn)
                    elif msisdn == '':
                        break
                    else:
                        print(f'{msisdn} is an Invalid chat_id')
                self.chatId = self.create_group(chat_ids)
            elif not self.group_pattern.match(self.chatId) and not self.chatid_pattern.match(self.chatId):
                raise RuntimeError(f'{self.chatId} is invalid, use .us or .gs')

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
