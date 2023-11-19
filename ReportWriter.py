""" ReportWriter module with classes for writing HTML and PDF files. """
from datetime import date
from Processor import CollectionProcessor


class WriterHtml(CollectionProcessor):
    """
    The WriterHtml class extends the CollectionProcessor class.
    It provides methods for writing HTML files.
    """

    def __init__(self, processor=None):
        """
        Initialize the WriterHtml class with the next processor.
        """
        super().__init__(processor)

    def process_impl(self, data):
        """
        Write the given data to an HTML file.
        The filename is generated based on the current date and the vendor name from the data.
        The data buffer is written to the file.
        The filename is returned.
        """
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data['buffer'])
        return filename


class WriterPdf(CollectionProcessor):
    """
    The WriterPdf class extends the CollectionProcessor class.
    It provides methods for writing PDF files.
    """

    def __init__(self, processor=None):
        """
        Initialize the WriterPdf class with the next processor.
        """
        super().__init__(processor)

    def process_impl(self, data):
        """
        Write the given data to a PDF file.
        The filename is generated based on the current date and the vendor name from the data.
        The data buffer is written to the file using the weasyprint HTML to PDF converter.
        The filename is returned.
        """
        from weasyprint import HTML
        filename = f"output/{date.today().strftime('%y-%m-%d')}_{data['vendorName']}.pdf"
        HTML(string=data['buffer']).write_pdf(filename)
        return filename
