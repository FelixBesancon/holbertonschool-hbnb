#!/usr/bin/python3
"""
Review model module.

This module defines the Review class, which represents a review
left by a user for a place in the HBnB application.
"""
from .basemodel import BaseModel


class Review(BaseModel):
    """
    Represents a review of a place in the HBnB platform.

    A review:
        - Contains a rating (1 to 5)
        - Contains a text
        - Has one author (user_id)
        - Refers to one place (place_id)
    """

    def __init__(self, *, rating, text, user_id, place_id):
        """
        Initialize a new Review instance.

        Args:
            rating (int): Rating of the place (1 to 5).
            text (str): Text content of the review.
            user_id (str): UUID string of the author.
            place_id (str): UUID string of the reviewed place.

        Raises:
            TypeError: If a field type is invalid.
            ValueError: If a field value is invalid.
        """
        # Validate ids
        self._validate_uuid(user_id, "user_id")
        self._validate_uuid(place_id, "place_id")

        # Validate rating
        if not isinstance(rating, int):
            raise TypeError("Rating must be an integer")
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # Validate text
        if not isinstance(text, str):
            raise TypeError("Text must be a string")
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("Text must not be empty")

        super().__init__()

        self.user_id = user_id
        self.place_id = place_id
        self.rating = rating
        self.text = cleaned_text
