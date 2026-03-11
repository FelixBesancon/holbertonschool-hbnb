from app import db
from app.models.basemodel import BaseModel


class Amenity(BaseModel):
    """
    SQLAlchemy model representing an amenity in the HBnB application.

        An amenity describes a feature or service that can be associated with a
        place, such as WiFi, parking, air conditioning, etc.

        The class inherits from BaseModel, which provides common attributes
        and functionality such as:
            - id (UUID primary key)
            - created_at timestamp
            - updated_at timestamp
            - validation helpers (e.g. is_max_length, is_between)

    Relationships with other entities (such as Place) are intentionally not
    implemented at this stage and will be added in later tasks.
    """

    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        """
        Initialize an Amenity instance.

        Args:
            name (str): Name of the amenity. Must be a non-empty string with
                        a maximum length of 50 characters.
        """
        self.set_name(name)

    def set_name(self, value):
        """
        Validate and assign the amenity name.

        Args:
            value (str): Name of the amenity.

        Raises:
            TypeError: If the name is not a string.
            ValueError: If the name is empty or exceeds the allowed length.
        """
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        if not value:
            raise ValueError("Name cannot be empty")
        super().is_max_length('Name', value, 50)
        self.name = value

    def to_dict(self):
        """
        Serialize the Amenity object into a dictionary.

        This representation is typically used for API responses
        or JSON serialization.

        Returns:
            dict: A dictionary containing the amenity attributes.

        """
        return {
            'id': self.id,
            'name': self.name
        }
