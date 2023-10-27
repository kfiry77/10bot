from TenbisLogic import *
from CouponsFormatter import *
from ReportWriter import *
from sys import platform
import sys


def main(argv):
    ten_bis = Tenbis()

    budget_available = ten_bis.is_budget_available()
    print('budget available=', budget_available)
    if budget_available:
        ten_bis.buy_coupon(40)
    coupons = ten_bis.get_unused_coupons()

    formatter = CouponFormatter(coupons)
    if platform == "win32":
        writer = ReportWriterHtml()
    else:
        writer = ReportWriterPdf()

    for r in coupons.values():
        formatted_string = formatter.format_orders(r['orders'], r['restaurantName'])
        writer.write(formatted_string, r['vendorName'])


if __name__ == '__main__':
    main(sys.argv[1:])
