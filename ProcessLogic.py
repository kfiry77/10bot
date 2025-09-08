"""
This module contains the ProcessLogic class which extends the Processor class.
It provides methods for managing purchases.
"""
from HolidaysDatabase import HolidaysDatabase
from PickleSerializer import PickleSerializer
from TenbisLogic import Tenbis
from Processor import Processor

class ProcessLogic(Processor):
    """
    The ProcessLogic class extends the Processor class.
    It manages the logic for processing data
    """
    def __init__(self, args, next_processors=None):
        """
        Initialize the ProcessLogic class with the given arguments and next processors.
        """
        super().__init__(next_processors)
        self.holidays_db = HolidaysDatabase()
        self.ten_bis = Tenbis(args)
        self.buy = args.buy

    @staticmethod
    def compare_coupons_files(c1, c2):
        """
        Compare two coupon files. Return False if they are not identical, True otherwise.
        """
        if len(c1) != len(c2) or c1.keys() != c2.keys():
            return False

        for k in c1.keys():
            l1 = c1[k]['orders']
            l2 = c2[k]['orders']

            if len(l2) != len(l1):
                return False

            coupons_list1 = sorted([item['barcode'] for item in l1])
            coupons_list2 = sorted([item['barcode'] for item in l1])
            if coupons_list1 != coupons_list2:
                return False

        return True

    def process_impl(self, data):
        """
        Process the given data. Manage purchases and reports based on the data and the current budget.
        """
        send_report = False
        if data.disable_purchase:
            self.logger.info('Purchase is disabled today.')
        elif not self.holidays_db.is_working_day():
            self.logger.info('today is %s, skipping purchase', self.holidays_db.get_holiday_data()['eng_name'])
        else:
            credit_conversion_amount, daily_balance = self.ten_bis.budget_available()
            if credit_conversion_amount > 0 and self.buy == 'credit':
                self.logger.debug('%d Credit Conversion available, Transferring it to credit', credit_conversion_amount)
                self.ten_bis.load_remaining_amount_to_credit()
            elif daily_balance >= 40:
                self.logger.debug('%d NIS daily Budget available, Buying coupon', daily_balance)
                self.ten_bis.buy_coupon(40)
                send_report = True
            else:
                self.logger.info('No Budget available, skipping purchase')

        coupons = self.ten_bis.get_unused_coupons()
        coupons_pickle = PickleSerializer('coupons')
        if coupons_pickle.exists():
            prev_coupons = coupons_pickle.load()
            send_report = send_report or not self.compare_coupons_files(prev_coupons, coupons)
        else:
            send_report = True
        coupons_pickle.create(coupons)
        if not send_report:
            self.logger.info('No report changes, publish will be skipped')
            return {}
        return coupons.values()
