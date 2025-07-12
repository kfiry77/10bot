"""
This module contains the ProcessLogic class which extends the Processor class.
It provides methods for managing purchases.
"""
from HolidaysDatabase import HolidaysDatabase
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

    def process_impl(self, data):
        """
        Process the given data. Manage purchases and reports based on the data and the current budget.
        """
        if data.disable_purchase:
            self.logger.info('Purchase is disabled today.')
        elif not self.holidays_db.is_working_day():
            self.logger.info('today is %s, skipping purchase', self.holidays_db.get_holiday_data()['eng_name'])
        else:
            budget = self.ten_bis.budget_available()
            if budget > 0:
                self.logger.debug('%d Budget available, Transferring it to credit', budget)
                self.ten_bis.load_remaining_amount_to_credit()
   #            self.ten_bis.buy_coupon(40)
            else:
                self.logger.info('No Budget available, skipping purchase')
