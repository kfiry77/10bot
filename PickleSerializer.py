"""
This module contains the PickleSerializer class which provides methods for
serializing and deserializing Python objects using the pickle module.
"""
import pickle
import os


class PickleSerializer:
    """
    A class used to serialize and deserialize Python objects using the pickle module.

    ...

    Attributes
    ----------
    path : str
        a formatted string that represents the path where the serialized object will be stored

    Methods
    -------
    exists():
        Checks if the serialized object already exists in the path.
    load():
        Deserializes and returns the Python object from the path if it exists.
    create(obj):
        Serializes and stores the Python object to the path.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the PickleSerializer object.

        Parameters
        ----------
            name : str
                the name of the file where the serialized object will be stored
        """
        self.path = f"{os.getcwd()}/state/{name}.pickle"

    def exists(self):
        """
        Checks if the serialized object already exists in the path.

        Returns
        -------
        bool
            True if the file exists, False otherwise
        """
        return os.path.exists(self.path)

    def load(self):
        """
        Deserializes and returns the Python object from the path if it exists.

        Returns
        -------
        obj
            the deserialized Python object if the file exists, None otherwise
        """
        if not self.exists():
            return None
        with open(self.path, 'rb') as session_file:
            obj = pickle.load(session_file)
            return obj

    def create(self, obj):
        """
        Serializes and stores the Python object to the path.

        Parameters
        ----------
        obj : object
            the Python object to be serialized
        """
        with open(self.path, 'wb') as session_file:
            pickle.dump(obj, session_file)
