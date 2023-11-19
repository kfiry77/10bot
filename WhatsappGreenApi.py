""" This module contains the WhatsappGreenApi class for interacting with the Green API. """

import re
import json
import requests
from PickleSerializer import PickleSerializer


class WhatsappGreenApi:
    """
    The WhatsappGreenApi class provides methods for interacting with the Green API.
    It includes methods for authentication, creating groups, getting chat history, and sending messages.
    """
    # Regular expressions for validating group and chat IDs
    group_pattern = re.compile(r'^\d{18}@g\.us$')
    chatid_pattern = re.compile(r'^\d{12}@c\.us$')
    request_timeout = 60

    def __init__(self, args):
        self.chatId = None
        self.apiTokenInstance = None
        self.idInstance = None
        self.host = 'api.green-api.com'
        self.args = args
        self.authenticated = self.auth()
        if not self.authenticated:
            print('Error Authenticating to Green api, publisher will be skipped')

    def create_group(self, chat_ids):
        """ Create a group with the given chat_ids and return the group ID"""
        url = f'https://{self.host}/waInstance{self.idInstance}/createGroup/{self.apiTokenInstance}'
        payload = {'groupName': "10Bot", 'chatIds': chat_ids}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, timeout=self.request_timeout, headers=headers,
                                 data=json.dumps(payload, sort_keys=False))
        if response.status_code != 200:
            raise RuntimeError(f'Green API Error:{response.status_code} message:{response.text}')

        resp_json = json.loads(response.text)
        if not resp_json['created']:
            raise RuntimeError(f'Green API Error:{response.status_code} message:{response.text}')
        print(f"WhatsApp Group created Id={resp_json['chatId']}, invitelink={resp_json['groupInviteLink']}")
        return resp_json['chatId']

    def auth(self):
        """ Authenticate to the Green API"""
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
            elif not self.group_pattern.match(self.chatId) and not self.chatid_pattern.match(self):
                raise RuntimeError(f'{self.chatId} is invalid, use dddd@c.us or dddd@g.us')

            auth_pickle.create({
                'idInstance': self.idInstance,
                'apiTokenInstance': self.apiTokenInstance,
                'chatId': self.chatId
            })

        url = f'https://{self.host}/waInstance{self.idInstance}/getStateInstance/{self.apiTokenInstance}'

        try:
            response = requests.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException as e:
            print(f'Error {e}Authenticating to Green api, publisher will be skipped')
            return False
        return response.status_code == 200 and json.loads(response.text)['stateInstance'] == 'authorized'

    def get_chat_history(self, count=100):
        """ Get chat history from the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/getChatHistory/{self.apiTokenInstance}'
        payload = {'chatId': self.chatId, 'count': count}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, timeout=self.request_timeout, headers=headers,
                                 data=json.dumps(payload, sort_keys=False))
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            return []
        return json.loads(response.text.encode('utf8'))

    def send_file_by_upload(self, filename):
        """ Send file to the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/sendFileByUpload/{self.apiTokenInstance}'
        payload = {'chatId': self.chatId, 'caption': '10Bot Coupon'}
        with open(filename, 'rb') as upload_file:
            files = {'file': upload_file}
            response = requests.post(url, timeout=self.request_timeout, data=payload, files=files)
        if self.args.verbose:
            print(response.status_code)
            print(response.text)
        return response.status_code == 200

    def send_message(self, message):
        """ Send message to the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/sendMessage/{self.apiTokenInstance}'
        payload = {'chatId': self.chatId, 'message': message}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, timeout=self.request_timeout,
                                 headers=headers, data=json.dumps(payload, sort_keys=False))
        print(response.status_code)
        print(response.text)
        return response.status_code == 200
