"""
Interface definition for WhatsApp API server such as GreenAPI
"""

from abc import ABC, abstractmethod

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
    def send_message(self, chat_id, message):
        """Send a message to the chatId"""
