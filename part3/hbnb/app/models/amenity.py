#!/usr/bin/python3
"""
Amenity model module.

This module defines the Amenity class, which represents an amenity
(e.g., Wi-Fi, Parking, Pool...) that can be associated with a place
in the HBnB application.
"""

from .basemodel import BaseModel


class Amenity(BaseModel):
    """
    Represents an amenity in the HBnB platform.

    An amenity:
        - Has a name (required, max 50 characters)
        - Can be associated with multiple places
    """

    def __init__(self, name):
        """
        Initialize a new Amenity instance.

        Args:
            name (str): The name of the amenity (required, max 50 chars).

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is empty or exceeds 50 characters.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

        name = name.strip()

        if name == "":
            raise ValueError("Name cannot be empty")

        if len(name) > 50:
            raise ValueError("Name must be 50 characters maximum")

        super().__init__()

        self.name = name
