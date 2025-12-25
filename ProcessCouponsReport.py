"""
This module contains the ProcessCouponsReport class which extends the Processor class.
It provides methods for processing coupon reports. 
"""
from PickleSerializer import PickleSerializer
from TenbisLogic import Tenbis
from Processor import Processor

class ProcessCouponsReport(Processor):
    """
    The ProcessCouponsReport class extends the Processor class.
    It manages the logic for processing data and managing reports.
    """

    def __init__(self, args, next_processors=None):
        """
        Initialize the ProcessCouponsReport class with the given arguments and next processors.
        """
        super().__init__(next_processors)
        self.ten_bis = Tenbis(args)

    def process_impl(self, data):
        """
        Process and Manage reports.
        Return the values of the coupons if a report should be sent, an empty dictionary otherwise.
        """
        coupons = self.ten_bis.get_unused_coupons()
        coupons_pickle = PickleSerializer('coupons')
        coupons_pickle.create(coupons)
        return coupons.values()
