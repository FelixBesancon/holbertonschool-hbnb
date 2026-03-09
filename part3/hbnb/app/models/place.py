#!/usr/bin/python3
"""
Place model module.

This module defines the Place class, which represents a property listing
in the HBnB application.

The Place model stores relationships using identifiers:
- owner_id (str UUID)
- amenity_ids (list[str UUID])
- review_ids (list[str UUID])
"""


from .basemodel import BaseModel


class Place(BaseModel):
    """
    Represents a place (property listing) in the HBnB platform.

    A place:
        - Has one owner (owner_id: UUID string)
        - Can have multiple reviews (stored as review IDs)
        - Can have multiple amenities (stored as amenity IDs)
        - Has a title, optional description, price, and location (lat/long)
    """

    def __init__(
        self, *, owner_id, title, description="", price=0,
        latitude=0, longitude=0, amenities=None
    ):
        """
        Initialize a new Place instance.

        Args:
            owner_id (str): UUID string of the owner (required).
            title (str): Place title (required, max 100 chars).
            description (str | None): Optional description.
            price (int | float): Price per night (must be > 0).
            latitude (int | float): Latitude (-90 to 90).
            longitude (int | float): Longitude (-180 to 180).
            amenities (list[str] | None): Optional list of
            amenity UUID strings.

        Raises:
            TypeError: If a field type is invalid.
            ValueError: If a field value is invalid.
        """
        # -------------------------
        # Validate owner_id
        # -------------------------
        if not isinstance(owner_id, str):
            raise TypeError("owner_id must be a string")
        self._validate_uuid(owner_id, "owner_id")

        # -------------------------
        # Validate title
        # -------------------------
        if not isinstance(title, str):
            raise TypeError("Title must be a string")
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 100:
            raise ValueError("Title must be <= 100 characters")

        # -------------------------
        # Validate description
        # -------------------------
        if description is None:
            description = ""
        if not isinstance(description, str):
            raise TypeError("Description must be a string")
        description = description.strip()

        # -------------------------
        # Validate price
        # -------------------------
        if not isinstance(price, (int, float)) or type(price) is bool:
            raise TypeError("Price must be a number")
        if price <= 0:
            raise ValueError("Price must be positive")

        # -------------------------
        # Validate latitude
        # -------------------------
        if not isinstance(latitude, (int, float)) or type(latitude) is bool:
            raise TypeError("Latitude must be a number")
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("Latitude must be between -90 and 90")

        # -------------------------
        # Validate longitude
        # -------------------------
        if not isinstance(longitude, (int, float)) or type(longitude) is bool:
            raise TypeError("Longitude must be a number")
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError("Longitude must be between -180 and 180")

        # -------------------------
        # Validate amenities list (optional)
        # -------------------------
        if amenities is None:
            amenities = []

        if not isinstance(amenities, list):
            raise TypeError("amenities must be a list of UUID strings")

        for aid in amenities:
            if not isinstance(aid, str):
                raise TypeError("Each amenity id must be a string")
            self._validate_uuid(aid, "amenity_id")

        super().__init__()

        self.owner_id = owner_id
        self.title = title
        self.description = description
        self.price = float(price)
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.review_ids = []
        self.amenity_ids = list(amenities)

    # ------------------------------------------------------------
    # -------------------- RELATIONSHIP HELPERS -------------------
    # ------------------------------------------------------------
    def add_review_id(self, review_id):
        """
        Associate a review identifier with this place.

        Args:
            review_id (str): UUID string of a review.

        Raises:
            TypeError: If review_id is not a string.
            ValueError: If review_id is not a valid UUID.
        """
        if not isinstance(review_id, str):
            raise TypeError("review_id must be a string")
        self._validate_uuid(review_id, "review_id")
        if review_id not in self.review_ids:
            self.review_ids.append(review_id)

    def remove_review_id(self, review_id):
        """
        Remove an associated review identifier from this place.

        Args:
            review_id (str): UUID string of a review.

        Raises:
            TypeError: If review_id is not a string.
            ValueError: If review_id is not a valid UUID.
        """
        if not isinstance(review_id, str):
            raise TypeError("review_id must be a string")
        self._validate_uuid(review_id, "review_id")
        if review_id in self.review_ids:
            self.review_ids.remove(review_id)

    def add_amenity_id(self, amenity_id):
        """
        Associate an amenity identifier with this place.

        Args:
            amenity_id (str): UUID string of an amenity.

        Raises:
            TypeError: If amenity_id is not a string.
            ValueError: If amenity_id is not a valid UUID.
        """
        if not isinstance(amenity_id, str):
            raise TypeError("amenity_id must be a string")
        self._validate_uuid(amenity_id, "amenity_id")
        if amenity_id not in self.amenity_ids:
            self.amenity_ids.append(amenity_id)

    def remove_amenity_id(self, amenity_id):
        """
        Remove an associated amenity identifier from this place.

        Args:
            amenity_id (str): UUID string of an amenity.

        Raises:
            TypeError: If amenity_id is not a string.
            ValueError: If amenity_id is not a valid UUID.
        """
        if not isinstance(amenity_id, str):
            raise TypeError("amenity_id must be a string")
        self._validate_uuid(amenity_id, "amenity_id")
        if amenity_id in self.amenity_ids:
            self.amenity_ids.remove(amenity_id)

    # ------------------------------------------------------------
    # ----------- OPTIONAL OBJECT-BASED COMPATIBILITY -------------
    # ------------------------------------------------------------
    def add_review(self, review):
        """
        Backward-compatible helper to add a review object.

        Args:
            review (object): Review-like object with an 'id' attribute.

        Raises:
            TypeError: If review does not have an 'id' attribute.
        """
        if not hasattr(review, "id"):
            raise TypeError("Review must have an 'id' attribute")
        self.add_review_id(review.id)

    def remove_review(self, review):
        """
        Backward-compatible helper to remove a review object.

        Args:
            review (object): Review-like object with an 'id' attribute.

        Raises:
            TypeError: If review does not have an 'id' attribute.
        """
        if not hasattr(review, "id"):
            raise TypeError("Review must have an 'id' attribute")
        self.remove_review_id(review.id)

    def add_amenity(self, amenity):
        """
        Backward-compatible helper to add an amenity object.

        Args:
            amenity (object): Amenity-like object with an 'id' attribute.

        Raises:
            TypeError: If amenity does not have an 'id' attribute.
        """
        if not hasattr(amenity, "id"):
            raise TypeError("Amenity must have an 'id' attribute")
        self.add_amenity_id(amenity.id)

    def remove_amenity(self, amenity):
        """
        Backward-compatible helper to remove an amenity object.

        Args:
            amenity (object): Amenity-like object with an 'id' attribute.

        Raises:
            TypeError: If amenity does not have an 'id' attribute.
        """
        if not hasattr(amenity, "id"):
            raise TypeError("Amenity must have an 'id' attribute")
        self.remove_amenity_id(amenity.id)
