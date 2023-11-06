from TenbisLogic import Tenbis


class ProcessLogic:
    def __init__(self, args, publishers=[]):
        super().__init__()
        self.ten_bis = Tenbis(args)
        self.publishers = publishers

    def process(self):
        budget_available = self.ten_bis.is_budget_available()
        print('budget available=', budget_available)
        if budget_available:
            self.ten_bis.buy_coupon(40)
        coupons = self.ten_bis.get_unused_coupons()
        for vendor_coupon in coupons.values():
            for p in self.publishers:
                p.process(vendor_coupon)
