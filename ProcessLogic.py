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
            send_report = send_report or not self.ten_bis.compare_coupons_files(prev_coupons, coupons)
        else:
            send_report = True
        coupons_pickle.create(coupons)
        if not send_report:
            self.logger.info('No report changes, publish will be skipped')
            return {}
        return coupons.values()
