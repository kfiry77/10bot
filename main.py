from TenbisLogic import *
from CouponsFormatter import *
import sys


def main(argv):
    ten_bis = Tenbis()
    budget_available = ten_bis.is_budget_available()
    print('budget available=', budget_available)
    if budget_available:
        ten_bis.buy_coupon(40)
    coupons = ten_bis.get_unused_coupons()
    formatter = CouponFormatter(coupons)
    formatter.write_to_files()



if __name__ == '__main__':
    main(sys.argv[1:])
