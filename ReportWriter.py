from datetime import date
from Processor import *


class WriterHtml(Processor):

    def __init__(self, processor):
        super().__init__(processor)

    def process_impl(self, data):
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data['buffer'])
        return filename


class WriterPdf(Processor):

    def __init__(self, processor):
        super().__init__(processor)

    def process_impl(self, data):
        from weasyprint import HTML
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.pdf"
        HTML(string=data['buffer']).write_pdf(filename)
        return filename
