from ProcessLogic import *
from PublisherWhatappGreenAPI import *
from ReportWriter import *
from CouponsFormatter import CouponFormatter
import sys
import argparse


def main(argv):
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    args = parser.parse_args()

    formatter = CouponFormatter()
    publishers = [
                   ReportWriterHtml(formatter),
                   PublisherWhatsappGreenApi(ReportWriterPdf(formatter))
                 ]
    process_logic = ProcessLogic(args, publishers)
    process_logic.process()


if __name__ == '__main__':
    main(sys.argv[1:])
