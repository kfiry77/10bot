from Processor import *
from WhatsappGreenApi import *
from datetime import datetime


class ParsedCommands:
    def __init__(self):
        self.disable_purchase = False


class ChatCommandsReader(Processor):
    def __init__(self, whatsapp_api: WhatsappGreenApi, next_processors=None):
        super().__init__(next_processors)
        self.whatsAppApi = whatsapp_api

    def process_impl(self, data):
        messages = self.whatsAppApi.get_chat_history()
        print(f'fetch total of {len(messages)}')
        # Set the time to 5:00 AM
        now = datetime.now()
        min_date_time = datetime(now.year, now.month, now.day, 5, 0, 0)
        max_unix_time = int(min_date_time.timestamp())
        print(f'max_unix_time={max_unix_time}')
        filter_messages = sorted([m for m in messages if m['type'] == 'outgoing' and
                                  m['typeMessage'] in ['textMessage', 'extendedTextMessage'] and
                                  not m['sendByApi'] and
                                  m['timestamp'] >= max_unix_time and
                                  m['textMessage'].startswith("/")
                                  ], key=lambda m: m['timestamp'])
        print(f'relevant messages count={len(filter_messages)}')
        print(json.dumps(filter_messages, indent=4))

        parsed_command = ParsedCommands()
        for m in filter_messages:
            t = m['textMessage']
            if t == '/disable':
                parsed_command.disable_purchase = True
            elif t == '/enable':
                parsed_command.disable_purchase = False
        return parsed_command
