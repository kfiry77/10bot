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
    pdf_writer = None
    if platform != "win32":
        pdf_writer = ReportWriterPdf()
    html_writer = ReportWriterHtml()

    for r in coupons.values():
        formatted_string = formatter.format_orders(r['orders'], r['restaurantName'])
        html_writer.write(formatted_string, r['vendorName'])
        if pdf_writer is not None:
            pdf_writer.write(formatted_string, r['vendorName'])


if __name__ == '__main__':
    main(sys.argv[1:])
