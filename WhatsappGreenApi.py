""" This module contains the WhatsappGreenApi class for interacting with the Green API. """
import json
import requests
from PickleSerializer import PickleSerializer
from IWhatsappApi import IWhatsappApi

class WhatsappGreenApi(IWhatsappApi):
    """
    The WhatsappGreenApi class provides methods for interacting with the Green API.
    It includes methods for authentication, creating groups, getting chat history, and sending messages.
    """
    request_timeout = 60

    def __init__(self, args):
        super().__init__(args)
        self.apiTokenInstance = None
        self.idInstance = None
        self.host = 'api.green-api.com'
        self.authenticated = self.auth()
        if not self.authenticated:
            self.logger.warning('Error Authenticating to Green api, publisher will be skipped')

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
        else:
            print("*** Green API Auth ***")
            self.idInstance = input("Enter Instance Id: ")
            self.apiTokenInstance = input("Enter Api Token Instance: ")
            # chat_id is now handled by the base class
            auth_pickle.create({
                'idInstance': self.idInstance,
                'apiTokenInstance': self.apiTokenInstance
            })

        url = f'https://{self.host}/waInstance{self.idInstance}/getStateInstance/{self.apiTokenInstance}'

        try:
            response = requests.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException as e:
            self.logger.warning('Error Authenticating  Green api, publisher will be skipped')
            self.logger.debug(e)
            return False
        return response.status_code == 200 and json.loads(response.text)['stateInstance'] == 'authorized'

    def get_chat_history(self, count=100):
        """ Get chat history from the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/getChatHistory/{self.apiTokenInstance}'
        payload = {'chatId': self.chat_id, 'count': count}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, timeout=self.request_timeout, headers=headers,
                                 data=json.dumps(payload, sort_keys=False))
        if response.status_code != 200:
            self.logger.warning(response.status_code)
            self.logger.warning(response.text)
            return []
        return json.loads(response.text.encode('utf8'))

    def send_file_by_upload(self, filename):
        """ Send file to the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/sendFileByUpload/{self.apiTokenInstance}'
        payload = {'chatId': self.chat_id, 'caption': '10Bot Coupon'}
        with open(filename, 'rb') as upload_file:
            files = {'file': upload_file}
            response = requests.post(url, timeout=self.request_timeout, data=payload, files=files)
        self.logger.debug(response.status_code)
        self.logger.debug(response.text)
        return response.status_code == 200

    def send_message(self, message):
        """ Send message to the chatId"""
        url = f'https://{self.host}/waInstance{self.idInstance}/sendMessage/{self.apiTokenInstance}'
        payload = {'chatId': self.chat_id, 'message': message}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, timeout=self.request_timeout,
                                 headers=headers, data=json.dumps(payload, sort_keys=False))
        self.logger.debug(response.status_code)
        self.logger.debug(response.text)
        return response.status_code == 200
