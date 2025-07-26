"""
Interface definition for WhatsApp API server such as GreenAPI
"""
from abc import ABC, abstractmethod
import logging
import re
from PickleSerializer import PickleSerializer

class IWhatsappApi(ABC):
    """
    Abstract base class defining the interface for a WhatsApp API server (e.g., GreenAPI).

    Methods:
        create_group(chat_ids): Create a group with the given chat IDs and return the group ID.
        auth(): Authenticate to the Green API.
        get_chat_history(count=100): Retrieve chat history from the chat ID.
        send_file_by_upload(filename): Send a file to the chat ID.
        send_message(chat_id, message): Send a message to the chat ID.
    """

    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger('AppLogger')
        self.group_pattern = re.compile(r'^\d{18}@g\.us$')
        self.chatid_pattern = re.compile(r'^\d{12}@c\.us$')
        self.chat_id = self._load_or_init_chat_id()

    def _is_valid_chat_id(self, chat_id):
        return bool(self.chatid_pattern.match(chat_id) or self.group_pattern.match(chat_id))

    def _load_or_init_chat_id(self):
        chatid_pickle = PickleSerializer('ChatId')
        if chatid_pickle.exists():
            return chatid_pickle.load().get('chat_id')
        while True:
            chat_id = input("Enter ChatId/GroupId (Empty to skip): ")
            if not chat_id:
                return chat_id
            if self._is_valid_chat_id(chat_id):
                chatid_pickle.create({'chat_id': chat_id})
                return chat_id
            print(f"{chat_id} is an invalid chat_id. Use dddddddddddd@c.us or dddddddddddddddddd@g.us")

    @abstractmethod
    def create_group(self, chat_ids):
        """Create a group with the given chat_ids and return the group ID"""

    @abstractmethod
    def auth(self):
        """Authenticate to the Green API"""

    @abstractmethod
    def get_chat_history(self, count=100):
        """Get chat history from the chatId"""

    @abstractmethod
    def send_file_by_upload(self, filename):
        """Send a file to the chatId"""

    @abstractmethod
    def send_message(self, message):
        """Send a message to the chatId"""
