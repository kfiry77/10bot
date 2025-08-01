"""
This module contains the ProcessCouponsReport class which extends the Processor class.
It provides methods for comparing coupon files, processing data, and reports.
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
        Process and Manage reports.
        Return the values of the coupons if a report should be sent, an empty dictionary otherwise.
        """
        coupons = self.ten_bis.get_unused_coupons()
        coupons_pickle = PickleSerializer('coupons')
        if coupons_pickle.exists():
            prev_coupons = coupons_pickle.load()
            send_report = not self.compare_coupons_files(prev_coupons, coupons)
        else:
            send_report = True
        coupons_pickle.create(coupons)
        if not send_report:
            self.logger.info('No report changes, publish will be skipped')
            return {}
        return coupons.values()
