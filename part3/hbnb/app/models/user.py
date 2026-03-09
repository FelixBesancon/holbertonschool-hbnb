#!/usr/bin/python3
"""
User model module.

This module defines the User class, which represents a user
of the HBnB application.
"""


import re
from .basemodel import BaseModel


class User(BaseModel):
    """
    Represents a user of the HBnB platform.

    A user can:
        - Own multiple places
        - Write multiple reviews
        - Have administrative privileges
    """

    def __init__(
        self, first_name="", last_name="",
        email="", password=""
    ):
        """
        Initialize a new User instance.

        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            email (str): The user's email address.
            password (str): The user's password.
        """
        if not all(
            isinstance(data, str)
            for data in (first_name, last_name, email, password)
        ):
            raise TypeError("Invalid data: all fields must be strings")

        first_name = first_name.strip()
        last_name = last_name.strip()

        if not first_name or len(first_name) == 0:
            raise ValueError("First name is required")
        if len(first_name) > 50:
            raise ValueError("First name must not exceed 50 characters")

        if not last_name:
            raise ValueError("Last name is required")
        if len(last_name) > 50:
            raise ValueError("Last name must not exceed 50 characters")

        if not email:
            raise ValueError("Email is required")

    # if not password:
    #    raise ValueError("Password is required")

        super().__init__()

        self.first_name = first_name
        self.last_name = last_name
        self.email = self._validate_email(email)
    # self.password = self._validate_password(password)
        self.password = password
        self.is_admin = False
        self.place_ids = []
        self.review_ids = []

    @staticmethod
    def _validate_email(email):
        """
        Validate email rules.

        Args:
            email (str): Email to validate.

        Raises:
            ValueError: If the email does not meet structural requirements.
        """
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Email must be valid")
        return email

    @staticmethod
    def _validate_password(password):
        """
        Validate password strength rules.

        Args:
            password (str): Password to validate.

        Raises:
            ValueError: If the password does not meet strength requirements.
        """
        if len(password) < 6:
            raise ValueError(
                "Password is too short: it must contain at least 6 characters"
            )

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")

        if not any(char.isupper() for char in password):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        return password

    def add_place(self, place):
        """
        Associate a place with this user.

        Args:
            place (Place): The place object to associate.

        Adds the place ID to the user's place_ids list
        if it is not already present.
        """
        if not hasattr(place, "id"):
            raise TypeError("Place must have an 'id' attribute")
        self._validate_uuid(place.id, "place.id")
        if place.id not in self.place_ids:
            self.place_ids.append(place.id)

    def remove_place(self, place):
        """
        Remove an associated place from this user.

        Args:
            place (Place): The place object to remove.

        Removes the place ID from the user's place_ids list
        if it exists.
        """
        if not hasattr(place, "id"):
            raise TypeError("Place must have an 'id' attribute")
        self._validate_uuid(place.id, "place.id")
        if place.id in self.place_ids:
            self.place_ids.remove(place.id)

    def add_review(self, review):
        """
        Associate a review with this user.

        Args:
            review (Review): The review object to associate.

        Adds the review ID to the user's review_ids list
        if it is not already present.
        """
        if not hasattr(review, "id"):
            raise TypeError("Review must have an 'id' attribute")
        self._validate_uuid(review.id, "review.id")
        if review.id not in self.review_ids:
            self.review_ids.append(review.id)

    def remove_review(self, review):
        """
        Remove an associated review from this user.

        Args:
            review (Review): The review object to remove.

        Removes the review ID from the user's review_ids list
        if it exists.
        """
        if not hasattr(review, "id"):
            raise TypeError("Review must have an 'id' attribute")
        self._validate_uuid(review.id, "review.id")
        if review.id in self.review_ids:
            self.review_ids.remove(review.id)
