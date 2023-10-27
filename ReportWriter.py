from abc import ABC, abstractmethod
from datetime import date


class ReportWriter(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def write(self, buffer, base_name):
        pass


class ReportWriterHtml(ReportWriter):

    def write(self, buffer, base_name):
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{base_name}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(buffer)


class ReportWriterPdf(ReportWriter):

    def write(self, buffer, base_name):
        from weasyprint import HTML
        HTML(string=buffer).write_pdf(f"output/{date.today().strftime('%y-%m-%d')}_{base_name}.pdf")
