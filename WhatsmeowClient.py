""" This module contains the WhatsappNeonize class for interacting with WhatsApp using the Whatsmeow library. """
from datetime import datetime
import requests
from IWhatsappApi import IWhatsappApi
from PickleSerializer import PickleSerializer

class WhatsmeowClient(IWhatsappApi):
    """
    The WhatsmeowClient class provides methods for interacting with WhatsApp using the Whatsmeow library, and bridge.
    It includes methods for creating groups, and sending messages and files.
    """
    request_timeout = 60

    def __init__(self, args):
        """
        Initializes the WhatsApp client.
        """
        super().__init__(args)
        self.server_url = self._load_or_init_server_url()

    def _load_or_init_server_url(self):
        config_pickle = PickleSerializer('WhatsmeowClientConfig')
        if config_pickle.exists():
            return config_pickle.load().get('server_url', None)
        server_url = input("Enter Whatsmeow bridge server URL (e.g., http://localhost:8080): ")
        if server_url:
            config_pickle.create({'server_url': server_url})
        return server_url

    def create_group(self, chat_ids):
        """
        Creates a group with the given name and members.
        :param chat_ids: A list of member JIDs to add to the group.
        :return: The JID of the newly created group.
        """
        return chat_ids

    def send_message(self, message):
        url = f"{self.server_url}/api/send"
        payload = {
            "recipient": self.chat_id, "message": message
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload,
            timeout = self.request_timeout, headers=headers)
        self.logger.debug(response)

    def send_file_by_upload(self, filename, caption=""):
        """
        Uploads and sends a file to the configured default chatId.
        :param filename: The path to the file to send.
        :param caption: The caption for the file.
        :return: True if successful, False otherwise.
        """
        self.logger.debug(filename + caption)
        return False

    def auth(self):
        """Authenticate"""

    def get_chat_history(self, count=30):
        """
        Fetch the last N messages from a specific chat via the WhatsApp bridge REST API.
        :param count: Number of messages to fetch (default 30)
        :return: List of message dicts, or raises an exception on error
        """
        url = f"{self.server_url}/api/messages"
        params = {"chat_jid": self.chat_id, "limit": str(count)}
        response = requests.get(url, params=params, timeout = self.request_timeout)
        self.logger.debug(response)
        response.raise_for_status()
        raw_messages = response.json()
        return [self._transform_message(m) for m in raw_messages]

    def _transform_message(self, m):
        """
        Transform Whatsmeow message format to the expected format.
        """
        # Convert unix timestamp to ISO8601 string with timezone +03:00
        return {
            'textMessage': m.get('Content'),
            'typeMessage': 'textMessage',
            'sendByApi': False,
            'timestamp': datetime.fromisoformat(m.get('Time')).timestamp(),
            'type': 'outgoing' if m.get('IsFromMe') else 'incoming'
        }

client = WhatsmeowClient(None)
client.send_message("Hi 10Bot!")
print(client.get_chat_history())
