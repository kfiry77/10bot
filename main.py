""" Main module to run the 10Bot application. """
import argparse
import datetime
import logging
import sys
from io import StringIO

from ChatCommandsReader import ChatCommandsReader
from CouponsFormatter import CouponFormatter
from ProcessLogic import ProcessLogic
from ReportWriter import WriterPdf, WriterHtml
from WhatsAppPublisher import WhatsAppPublisher
from WhatsappGreenApi import WhatsappGreenApi


def setup_logger(args):
    """
    Set up a logger with configurations for multiple handlers:
    - StreamHandler for logging to stdout with INFO level and a specific format.
    - FileHandler for writing logs to '10bot_app.log' with INFO level and a specific format.
    - FileHandler for writing debug logs to '10bot_debug.log' with DEBUG level and a specific format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger('AppLogger')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    verbose_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s '
                                          '(%(filename)s:%(funcName)s:%(lineno)d)')
    friendly_formatter = logging.Formatter('%(message)s')

    # Create a StreamHandler to send logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    stream_handler.setFormatter(verbose_formatter if args.verbose else friendly_formatter)
    logger.addHandler(stream_handler)

    # Create a StreamHandler to send logs to buffer
    log_stream = StringIO()
    string_io_handler = logging.StreamHandler(log_stream)
    string_io_handler.setLevel(logging.INFO)
    string_io_handler.setFormatter(friendly_formatter)
    logger.addHandler(string_io_handler)

    # Create a FileHandler to write logs to a file
    file_handler = logging.FileHandler('10bot_app.log', 'a', 'utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(verbose_formatter)
    logger.addHandler(file_handler)

    debug_handler = logging.FileHandler('10bot_debug.log', 'a', 'utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(verbose_formatter)
    logger.addHandler(debug_handler)

    return logger


def main():
    """
    The main function of the 10Bot application. It sets up the command line arguments, initializes the necessary
    classes, and starts the processing chain.
    """
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    parser.add_argument('-g', '--disablegreenapi', help='disables sending message to whatApp with GreenApi',
                        action='store_true')
    args = parser.parse_args()

    logger = setup_logger(args)
    logger.info('*** 10Bot started at %s ***', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    whatsapp_api = WhatsappGreenApi(args)
    process_chain = ChatCommandsReader(whatsapp_api,
                                       ProcessLogic(args,
                                                    CouponFormatter(
                                                        [
                                                            WriterHtml(),
                                                            WriterPdf(
                                                                WhatsAppPublisher(args, whatsapp_api))
                                                        ])))
    process_chain.process()

    logger.info('*** 10Bot ended ***')
    # send report to whatsup.
    whatsapp_api.send_message(whatsapp_api.chatId, logger.handlers[1].stream.getvalue())


if __name__ == '__main__':
    main()
