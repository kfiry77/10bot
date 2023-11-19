from abc import ABC, abstractmethod


class Processor(ABC):
    """
    The Processor class is an abstract base class that provides a template for processing data.
    It can be extended by other classes to implement specific processing logic.
    """

    def __init__(self, next_processor=None):
        """
        Initialize the Processor class with the next processor.
        If next_processor is None, an empty list is assigned to self.next_processors.
        If next_processor has a length, it is assigned to self.next_processors.
        If next_processor does not have a length, it is wrapped in a list and assigned to self.next_processors.
        """
        super().__init__()

        if next_processor is None:
            self.next_processors = []
        elif hasattr(next_processor, '__len__'):
            self.next_processors = next_processor
        else:
            self.next_processors = [next_processor]

    @abstractmethod
    def process_impl(self, data):
        """
        Abstract method to be implemented by subclasses.
        It should process the given data and return the processed data.
        """
        pass

    def process(self, data=None):
        """
        Process the given data using the process_impl method.
        Then, the processed data is passed to the next processors (if any) and their results are collected.
        If there is only one result, it is returned directly. Otherwise, a list of results is returned.
        """
        processed_data = self.process_impl(data)
        result_data = []
        for p in self.next_processors:
            result_data.append(p.process(processed_data))
        return result_data if len(result_data) != 1 else result_data[0]


class CollectionProcessor(Processor, ABC):
    """
    The CollectionProcessor class extends the Processor class.
    It provides a template for processing collections of data.
    """

    def __init__(self, next_processor=None):
        """
        Initialize the CollectionProcessor class with the next processor.
        """
        super().__init__(next_processor)

    def process(self, data_array=None):
        """
        Process each item in the given data array using the process_impl method.
        Then, the processed data is passed to the next processors (if any) and their results are collected.
        If there is only one result, it is returned directly. Otherwise, a list of results is returned.
        """
        processed_data = []
        for data in data_array:
            processed_data.append(self.process_impl(data))
        result_data = []
        for p in self.next_processors:
            result_data.append(p.process(processed_data))
        return result_data if len(result_data) != 1 else result_data[0]
