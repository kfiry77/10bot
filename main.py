from TenbisLogic import *
import sys


def main(argv):
    ten_bis = Tenbis()
    budget_available = ten_bis.is_budget_available()
    print('budget available=', budget_available)
    if budget_available:
        ten_bis.buy_coupon(40)


if __name__ == '__main__':
    main(sys.argv[1:])
