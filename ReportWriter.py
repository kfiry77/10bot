from datetime import date
from Processor import *


class WriterHtml(Processor):

    def __init__(self, processor=None):
        super().__init__(processor)

    def process_impl(self, vendor_coupons):
        ret_val = []
        for data in vendor_coupons:
            filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.html"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(data['buffer'])
            ret_val.append(filename)
        return ret_val


class WriterPdf(Processor):

    def __init__(self, processor=None):
        super().__init__(processor)

    def process_impl(self, vendor_coupons):
        from weasyprint import HTML
        ret_val = []
        for data in vendor_coupons:
            filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.pdf"
            HTML(string=data['buffer']).write_pdf(filename)
            ret_val.append(filename)
        return ret_val
