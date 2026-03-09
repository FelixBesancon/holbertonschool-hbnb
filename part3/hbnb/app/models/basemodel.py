#!/usr/bin/python3
"""
Base model module.

This module defines the BaseModel class, which provides common
attributes and behavior shared by all business entities
(User, Place, Review, Amenity).
"""


import uuid
from datetime import datetime


class BaseModel:
    """
    Base class for all HBnB entities.

    Provides:
        - A unique identifier (UUID)
        - Creation timestamp
        - Last update timestamp
        - Generic update mechanism
    """

    def __init__(self):
        """
        Initialize a new BaseModel instance.

        Automatically generates:
            - A unique UUID string as id
            - created_at timestamp
            - updated_at timestamp
        """
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """
        Update the updated_at timestamp.

        Should be called whenever the object is modified.
        """
        self.updated_at = datetime.now()

    def update(self, data):
        """
        Update the object's attributes using a dictionary.

        Args:
            data (dict): Dictionary containing attributes to update.

        Only existing attributes and non-protected attributes
        will be updated.
        The updated_at timestamp is refreshed automatically.
        """
        protected_fields = {
            "id",
            "created_at",
            "updated_at"
        }

        for key, value in data.items():
            if (
                hasattr(self, key) and
                key not in protected_fields
            ):
                setattr(self, key, value)

        self.save()  # Update the updated_at timestamp

    @staticmethod
    def _validate_uuid(value, field_name):
        """
         Validate that a given string is a valid UUID.

        Args:
            value (str): The value to validate.
            field_name (str): Field name for error reporting.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is not a valid UUID string.
        """
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        try:
            uuid.UUID(value)
        except ValueError as exc:
            raise ValueError(
                f"{field_name} must be a valid UUID"
            ) from exc
