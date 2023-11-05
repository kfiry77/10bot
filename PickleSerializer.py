import pickle
import os


class PickleSerializer:

    def __init__(self, name):
        self.path = f"{os.getcwd()}/{name}.pickle"

    def exists(self):
        return os.path.exists(self.path)

    def load(self):
        if not self.exists():
            return None
        with open(self.path, 'rb') as session_file:
            obj = pickle.load(session_file)
            return obj

    def create(self, obj):
        with open(self.path, 'wb') as session_file:
            pickle.dump(obj, session_file)
