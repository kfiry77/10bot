""" WhatsAppPublisher module """
from IWhatsappApi import IWhatsappApi
from Processor import CollectionProcessor


class WhatsAppPublisher(CollectionProcessor):
    """
    The WhatsAppPublisher class extends the CollectionProcessor class.
    It provides methods for publishing files to WhatsApp using the WhatsappGreenApi.
    """

    def __init__(self, args, whatsapp_api: IWhatsappApi, processor=None):
        """
        Initialize the WhatsAppPublisher class with the given arguments, WhatsappGreenApi, and next processor.
        """
        super().__init__(processor)
        self.args = args
        self.whatsAppApi = whatsapp_api

    def process_impl(self, data):
        """
        Publish the given filename to WhatsApp.
        If the WhatsappGreenApi is not authenticated or if it is disabled, a message is printed and the method returns.
        If the file is successfully published, the result of the send_file_by_upload method is returned.
        """
        if not self.whatsAppApi.authenticated:
            print('Whatsapp is not authenticated, publish will be skipped')
            return False

        if self.args.disableWhatsapp:
            print("Whatsapp is disabled, publish will be skipped.")
            return False
        filename = data
        return self.whatsAppApi.send_file_by_upload(filename)
