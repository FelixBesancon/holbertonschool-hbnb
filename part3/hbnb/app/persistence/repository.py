#!/usr/bin/python3
"""
Repository module.

Defines an abstract base repository interface and an in-memory
implementation used for temporary object storage.
"""


from abc import ABC, abstractmethod


class Repository(ABC):
    """
    Abstract base class defining the repository interface.

    This class specifies the standard operations required for
    storing and retrieving domain objects.
    """
    @abstractmethod
    def add(self, obj):
        """
        Add an object to the repository.

        Args:
            obj: The object instance to store.
        """
        pass

    @abstractmethod
    def get(self, obj_id):
        """
        Retrieve an object by its unique identifier.

        Args:
            obj_id (str): The unique identifier of the object.

        Returns:
            The object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_all(self):
        """
        Retrieve all stored objects.

        Returns:
            list: A list containing all stored objects.
        """
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """
        Update an existing object in the repository.

        Args:
            obj_id (str): The unique identifier of the object.
            data (dict): A dictionary of attributes to update.
        """
        pass

    @abstractmethod
    def delete(self, obj_id):
        """
        Remove an object from the repository.

        Args:
            obj_id (str): The unique identifier of the object.
        """
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve the first object matching a given attribute value.

        Args:
            attr_name (str): The attribute name to search by.
            attr_value: The expected value of the attribute.

        Returns:
            The first matching object if found, otherwise None.
        """
        pass


class InMemoryRepository(Repository):
    """
    In-memory implementation of the Repository interface.

    Stores objects in a dictionary using their unique ID as the key.
    This implementation is temporary and intended for development
    before integrating a database-backed persistence layer.
    """
    def __init__(self):
        """Initialize the in-memory storage."""
        self._storage = {}

    def add(self, obj):
        """
        Store an object in memory.

        Args:
            obj: The object instance to store. Must have an 'id' attribute.
        """
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """
        Retrieve an object by its ID.

        Args:
            obj_id (str): The object's unique identifier.

        Returns:
            The object if found, otherwise None.
        """
        return self._storage.get(obj_id)

    def get_all(self):
        """
        Retrieve all stored objects.

        Returns:
            list: A list of all stored objects.
        """
        return list(self._storage.values())

    def update(self, obj_id, data):
        """
        Update an existing object using provided data.

        Args:
            obj_id (str): The object's unique identifier.
            data (dict): Dictionary of attributes to update.
        """
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        """
        Delete an object from storage.

        Args:
            obj_id (str): The object's unique identifier.
        """
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve the first object that matches a given attribute value.

        Args:
            attr_name (str): The attribute name to check.
            attr_value: The expected value of the attribute.

        Returns:
            The first matching object if found, otherwise None.
        """
        return next(
            (
                obj
                for obj in self._storage.values()
                if getattr(obj, attr_name) == attr_value
            ),
            None
        )
