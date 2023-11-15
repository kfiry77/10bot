from abc import ABC, abstractmethod


class Processor(ABC):
    def __init__(self, next_processor=None):
        super().__init__()

        if next_processor is None:
            self.next_processors = []
        elif hasattr(next_processor, '__len__'):
            self.next_processors = next_processor
        else:
            self.next_processors = [next_processor]


    @abstractmethod
    def process_impl(self, data):
        pass

    def process(self, data=None):
        processed_data = self.process_impl(data)
        result_data = []
        for p in self.next_processors:
            result_data.append(p.process(processed_data))
        return result_data if len(result_data) != 1 else result_data[0]
