from ProcessLogic import *
from PublisherWhatappGreenAPI import *
from ReportWriter import *
from CouponsFormatter import CouponFormatter
import argparse


def main():
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    parser.add_argument('-g', '--disablegreenapi', help='disables sending message to whatApp with GreenApi',
                        action='store_true')
    args = parser.parse_args()

    process_logic = ProcessLogic(args,
                                 CouponFormatter(
                                     [
                                         WriterHtml(),
                                         WriterPdf(
                                             PublisherWhatsappGreenApi(args))
                                     ]))
    process_logic.process()


if __name__ == '__main__':
    main()
