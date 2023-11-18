from ProcessLogic import *
from ReportWriter import *
from CouponsFormatter import CouponFormatter
from WhatsAppPublisher import *
from ChatCommandsReader import *
import argparse


def main():
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    parser.add_argument('-g', '--disablegreenapi', help='disables sending message to whatApp with GreenApi',
                        action='store_true')
    args = parser.parse_args()

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


if __name__ == '__main__':
    main()
