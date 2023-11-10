from abc import ABC, abstractmethod


class Processor(ABC):
    def __init__(self, prev_processor=None):
        super().__init__()
        self.prev_processor = prev_processor

    @abstractmethod
    def process_impl(self, data):
        pass

    def process(self, data=None):
        new_data = data
        if self.prev_processor is not None:
            new_data = self.prev_processor.process(data)
        return self.process_impl(new_data)
