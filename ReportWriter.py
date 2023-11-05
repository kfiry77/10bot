from datetime import date
from ReportProcessor import *


class ReportWriterHtml(ReportProcessor):

    def __init__(self, processor, base_name):
        super().__init__(processor)
        self.base_name = base_name

    def process_impl(self, buffer):
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{self.base_name}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(buffer)


class ReportWriterPdf(ReportProcessor):

    def __init__(self, processor, base_name):
        super().__init__(processor)
        self.base_name = base_name

    def process_impl(self, buffer, base_name):
        from weasyprint import HTML
        HTML(string=buffer).write_pdf(f"output/{date.today().strftime('%y-%m-%d')}_{self.base_name}.pdf")
