import pickle
import os


class PickleSerializer:
    @classmethod
    def format_path(cls, name):
        return f"{os.getcwd()}/{name}.pickle"

    @classmethod
    def load(cls, name):
        with open(cls.format_path(name), 'rb') as session_file:
            obj = pickle.load(session_file)
            return obj

    @classmethod
    def create(cls, obj, name):
        with open(cls.format_path(name), 'wb') as session_file:
            pickle.dump(obj, session_file)
