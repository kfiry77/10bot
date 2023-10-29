from TenbisLogic import *
from CouponsFormatter import *
from ReportWriter import *
import sys
import argparse


def main(argv):
    parser = argparse.ArgumentParser(prog='10Bot')
    parser.add_argument('-v', '--verbose', help='enable detailed logging', action='store_true')
    parser.add_argument('-d', '--dryrun', help='Dry run to test all HTTP calls to NextAPI', action='store_true')
    args = parser.parse_args()

    ten_bis = Tenbis(args)
    budget_available = ten_bis.is_budget_available()
    print('budget available=', budget_available)
    if budget_available:
        ten_bis.buy_coupon(40)
    coupons = ten_bis.get_unused_coupons()

    formatter = CouponFormatter(coupons)
    pdf_writer = ReportWriterPdf()
    html_writer = ReportWriterHtml()

    for r in coupons.values():
        formatted_string = formatter.format_orders(r['orders'], r['restaurantName'])
        html_writer.write(formatted_string, r['vendorName'])
        if pdf_writer is not None:
            pdf_writer.write(formatted_string, r['vendorName'])


if __name__ == '__main__':
    main(sys.argv[1:])
