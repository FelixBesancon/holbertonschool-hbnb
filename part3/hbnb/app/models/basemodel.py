from app import db
import uuid
from datetime import datetime, timezone


class BaseModel(db.Model):
    """
    Abstract base class for all SQLAlchemy models in the HBnB application.

    This class provides common attributes and utility methods shared by
    all business entities. It ensures that every model inheriting from it
    has a unique identifier and timestamp tracking.

    Attributes:
        id (str):
            Unique identifier for the object, generated using UUID4.
        created_at (datetime):
            Timestamp indicating when the object was created.
        updated_at (datetime):
            Timestamp indicating the last time the object was updated.

    Notes:
        - The class is marked as abstract so SQLAlchemy does not create
          a database table for it.
        - Child classes inherit the columns and utility methods defined here.
    """

    __abstract__ = True

    id = db.Column(
        db.String(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
        )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
        )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
        )

    def save(self):
        """
        Update the `updated_at` timestamp.

        This method should be called whenever an object is modified to ensure
        that the `updated_at` field reflects the latest modification time.

        Note:
            This method does not commit changes to the database. The commit
            operation is handled by the repository layer.
        """
        self.updated_at = datetime.now(timezone.utc)

    def update(self, data):
        """
        Update attributes of the object using a dictionary of values.

        Args:
            data (dict): A dictionary containing attribute names and their
                         new values.

        Behavior:
            - Only attributes that already exist on the object are updated.
            - After updating the attributes, the `updated_at` timestamp
              is refreshed using the `save()` method.
        """
        protected_fields = {"id", "created_at", "updated_at"}

        for key, value in data.items():
            if key in protected_fields:
                raise ValueError(f"The {key} cannot be updated")
            if hasattr(self, key):
                setattr(self, key, value)

        self.save()

    def is_max_length(self, name, value, max_length):
        """
        Validate that a string does not exceed a maximum length.

        Args:
            name (str): Name of the attribute being validated.
            value (str): Value to validate.
            max_length (int): Maximum allowed length.

        Raises:
            ValueError: If the length of the value exceeds the allowed limit.
        """
        if len(value) > max_length:
            raise ValueError(f"{name} must be {max_length} characters max.")

    def is_between(self, name, value, min_value, max_value):
        """
        Validate that a numeric value falls within an inclusive range.

        Args:
            name (str): Name of the attribute being validated.
            value (int | float): Numeric value to validate.
            min_value (int | float): Minimum allowed value.
            max_value (int | float): Maximum allowed value.

        Raises:
            ValueError: If the value is outside the inclusive range.
        """
        if not min_value <= value <= max_value:
            raise ValueError(
                f"{name} must be between {min_value} and {max_value} included."
                )
