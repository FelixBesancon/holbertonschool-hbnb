from abc import ABC, abstractmethod
from app import db


class Repository(ABC):
    """
    Abstract base repository defining the persistence interface.

    This class provides a common contract for all repository
    implementations used in the HBnB application. It ensures a
    consistent API for basic CRUD operations and attribute-based queries,
    regardless of the underlying persistence mechanism.
    """

    @abstractmethod
    def add(self, obj):
        """
        Persist a new object in the repository.

        Args:
            obj: The object instance to store.
        """
        pass

    @abstractmethod
    def get(self, obj_id):
        """
        Retrieve a single object by its unique identifier.
        Args:
            obj_id (str): Unique identifier of the object.
        Returns:
            object | None: The matching object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_all(self):
        """
        Retrieve all objects stored in the repository.

        Returns:
            list: A list containing all stored objects.
        """
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """
        Update an existing object with new data.
        Args:
            obj_id (str): Unique identifier of the object to update.
            data (dict): Dictionary containing the new values.
        """
        pass

    @abstractmethod
    def delete(self, obj_id):
        """
        Delete an object from the repository.

        Args:
            obj_id (str): Unique identifier of the object to delete.
        """
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve an object by one of its attributes.

        Args:
            attr_name (str): Name of the attribute to query.
            attr_value: Expected value of the attribute.

        Returns:
            object | None: The first matching object if found, otherwise None.
        """
        pass


class SQLAlchemyRepository(Repository):
    """
    Generic SQLAlchemy-based repository implementation.

    This repository provides reusable CRUD operations for any SQLAlchemy
    model passed during initialization. It is used as a generic persistence
    layer for entities that do not require specialized query methods.

    Args:
        model: SQLAlchemy model class managed by this repository.
    """
    def __init__(self, model):
        """
        Initialize the repository with a specific SQLAlchemy model.

        Args:
            model: SQLAlchemy model class handled by the repository.
        """
        self.model = model

    def add(self, obj):
        """
        Add and commit a new object to the database.

        Args:
            obj: SQLAlchemy model instance to persist.
        """
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        """
        Retrieve an object by its unique identifier.

        Args:
            obj_id (str): Unique identifier of the object.

        Returns:
            object | None: The matching object if found, otherwise None.
        """
        return self.model.query.get(obj_id)

    def get_all(self):
        """
        Retrieve all objects of the repository model.

        Returns:
            list: A list of all persisted model instances.
        """
        return self.model.query.all()

    def update(self, obj_id, data):
        """
        Update an existing object and commit changes to the database.

        Args:
            obj_id (str): Unique identifier of the object to update.
            data (dict): Dictionary containing the new values.
        """
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()

    def delete(self, obj_id):
        """
        Delete an object from the database and commit the transaction.

        Args:
            obj_id (str): Unique identifier of the object to delete.
        """
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve the first object matching a given attribute value.

        Args:
            attr_name (str): Name of the attribute to query.
            attr_value: Expected value of the attribute.

        Returns:
            object | None: The first matching object if found, otherwise None.
        """
        return self.model.query.filter(
            getattr(self.model, attr_name) == attr_value
            ).first()
