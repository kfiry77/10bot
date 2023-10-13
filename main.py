from TenbisLogic import *
import sys


def main(argv):
    tenbis = Tenbis(argv[0])
    budget_available = tenbis.is_budget_available()
    print('budget available=', budget_available)
    if budget_available:
        tenbis.buy_coupon(40)


if __name__ == '__main__':
    main(sys.argv[1:])
