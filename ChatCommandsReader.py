"""
This module is responsible for reading the chat commands and return a ParsedCommands object.
It uses the WhatsappGreenApi to fetch the chat history and processes the messages to parse the commands.
"""

import json
from datetime import datetime
from Processor import Processor
from WhatsappGreenApi import WhatsappGreenApi


class ParsedCommands:
    """
    A class used to represent the parsed commands.

    Attributes
    ----------
    disable_purchase : bool
        a flag indicating whether the purchase is disabled or not
    """

    def __init__(self):
        self.disable_purchase = False


class ChatCommandsReader(Processor):
    """
    A class used to read and parse the chat commands.

    Attributes
    ----------
    whatsAppApi : WhatsappGreenApi
        an instance of the WhatsappGreenApi to interact with the WhatsApp API

    Methods
    -------
    process_impl(data)
        Processes the data to parse the commands.
    """

    def __init__(self, whatsapp_api: WhatsappGreenApi, next_processors=None):
        super().__init__(next_processors)
        self.whatsAppApi = whatsapp_api

    def process_impl(self, data):
        """
        Processes the data to parse the commands.

        Parameters
        ----------
        data : str
            The data to be processed.

        Returns
        -------
        ParsedCommands
            An instance of the ParsedCommands class with the parsed commands.
        """
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
