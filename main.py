""" Main module to run the 10Bot application. """
import argparse
import datetime
import logging
import sys
import http.client
from io import StringIO

from ChatCommandsReader import ChatCommandsReader
from CouponsFormatter import CouponFormatter
from ProcessLogic import ProcessLogic
from ReportWriter import WriterPdf, WriterHtml
from WhatsAppPublisher import WhatsAppPublisher
from ProcessCouponsReport import ProcessCouponsReport
#from WhatsappGreenApi import WhatsappGreenApi
from WhatsmeowClient import WhatsmeowClient

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
    logger.setLevel(logging.DEBUG)

    urllib3_logger = logging.getLogger('urllib3')
    requests_logger = logging.getLogger('requests')

    verbose_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s '
                                          '(%(filename)s:%(funcName)s:%(lineno)d)')
    friendly_formatter = logging.Formatter('%(message)s')

    # Create a StreamHandler to send logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    stream_handler.setFormatter(verbose_formatter if args.verbose else friendly_formatter)

    if args.verbose:
        http.client.HTTPConnection.debuglevel = 1
        urllib3_logger.addHandler(stream_handler)
        requests_logger.addHandler(stream_handler)
        urllib3_logger.setLevel(logging.DEBUG)
        requests_logger.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)

    # Create a StreamHandler to send logs to buffer
    if not args.disableWhatsapp:
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
    urllib3_logger.addHandler(debug_handler)
    requests_logger.addHandler(debug_handler)

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
    parser.add_argument('-g', '--disableWhatsapp', help='disables sending message to whatApp',
                        action='store_true')
    parser.add_argument('-r', '--couponsreport', help='create Shufersal coupon report only',
                        action='store_true')
    parser.add_argument('-b', '--buy', choices=['coupon','credit'], default='coupon',  help='defines if to buy coupon or to move to credit')
    args = parser.parse_args()

    logger = setup_logger(args)
    logger.info('*** 10Bot started at %s ***', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    whatsapp_api = WhatsmeowClient(args)
    try:
        if args.couponsreport:
            process_chain = ProcessCouponsReport(CouponFormatter(
                                                    [
                                                        WriterHtml(),
                                                        WriterPdf(WhatsAppPublisher(args, whatsapp_api))
                                                    ]))
        else:
            process_chain = ChatCommandsReader(whatsapp_api, ProcessLogic(args))
        process_chain.process()
    except RuntimeError:
        logger.info('Process resulted error')

    logger.info('*** 10Bot ended ***')
    # send report to whatsup.
    if not args.disableWhatsapp:
        whatsapp_api.send_message(logger.handlers[1].stream.getvalue())


if __name__ == '__main__':
    main()
