from abc import ABC, abstractmethod


class ReportProcessor(ABC):
    def __init__(self, next_processor=None):
        super().__init__()
        self.next_processor = next_processor

    @abstractmethod
    def process_impl(self, report):
        pass

    def process(self, report):
        if self.next_processor is not None:
            return self.next_processor.process(report)
