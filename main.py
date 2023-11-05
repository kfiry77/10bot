from ProcessLogic import *
from PublisherWhatappGreenAPI import *
import sys
import argparse


def main(argv):
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    args = parser.parse_args()

    publisher =
    process_logic = ProcessLogic()
    process_logic.publisher = PublisherWhatsappGreenApi()
    process_logic.process()


    publisher.publish()





if __name__ == '__main__':
    main(sys.argv[1:])
