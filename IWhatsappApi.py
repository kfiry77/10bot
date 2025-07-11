from abc import ABC, abstractmethod

class IWhatsappApi(ABC):
    @abstractmethod
    def create_group(self, chat_ids):
        """Create a group with the given chat_ids and return the group ID"""
        pass

    @abstractmethod
    def auth(self):
        """Authenticate to the Green API"""
        pass

    @abstractmethod
    def get_chat_history(self, count=100):
        """Get chat history from the chatId"""
        pass

    @abstractmethod
    def send_file_by_upload(self, filename):
        """Send file to the chatId"""
        pass

    @abstractmethod
    def send_message(self, chat_id, message):
        """Send message to the chatId"""
        pass
