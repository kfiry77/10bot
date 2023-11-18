from Processor import CollectionProcessor
import PublisherWhatappGreenAPI


class WhatsAppPublisher(CollectionProcessor):

    def __init__(self, args, whatsapp_api: PublisherWhatappGreenAPI, processor=None):
        super().__init__(processor)
        self.args = args
        self.whatsAppApi = whatsapp_api

    def process_impl(self, filename):
        if not self.whatsAppApi.authenticated:
            return False

        if self.args.disablegreenapi:
            print("Green API is disabled, publish will be skipped.")
            return

        return self.whatsAppApi.send_file_by_upload(filename)
