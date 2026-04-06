from app import db
from app.models.basemodel import BaseModel
from sqlalchemy.orm import validates

# Creation of a table to manage the many-to-many relationship
# between Place and Amenity
place_amenity = db.Table(
    'place_amenity',
    db.Column(
        'place_id', db.String(36),
        db.ForeignKey('places.id'),
        primary_key=True
        ),
    db.Column(
        'amenity_id', db.String(36),
        db.ForeignKey('amenities.id'),
        primary_key=True
    )
)


class Place(BaseModel):
    """
    SQLAlchemy model representing a place that can be listed
    in the HBnB application.

    This model defines the core attributes of a place, such as its title,
    description, price per night, and geographical coordinates.

    The class inherits from BaseModel, which provides common attributes
    and functionality such as:
        - id (UUID primary key)
        - created_at timestamp
        - updated_at timestamp
        - validation helpers (e.g. is_max_length, is_between)

    Relationships with other entities (User, Review, Amenity) are intentionally
    not implemented at this stage and will be added in later tasks.
    """

    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1024))
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id'),
        nullable=False)
    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        lazy='subquery',
        # No delete-orphan here
        # removing a Place only clears the join table, Amenities are preserved.
        backref=db.backref('places', lazy='select')
        )
    reviews = db.relationship(
        'Review', backref='place',
        lazy='select',
        # Deleting a Place automatically deletes all its associated Reviews.
        cascade='all, delete-orphan'
        )

    def __init__(self, title, price, latitude, longitude, description=None):
        """
        Initialize a Place instance.

        The constructor validates the provided values using dedicated
        setter methods before assigning them to the SQLAlchemy-mapped
        attributes.

        Args:
            title (str): Title of the place. Must be a non-empty string
                         with a maximum length of 100 characters.
            price (float | int): Price per night for the place. Must be a
                                 positive number.
            latitude (float | int): Geographic latitude of the place.
                                    Must be between -90 and 90.
            longitude (float | int): Geographic longitude of the place.
                                     Must be between -180 and 180.
            description (str, optional): Optional textual description of
                                         the place. Maximum length 1024.
        """
        self.title = title
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.description = description

    @validates("title")
    def validate_title(self, key, value):
        """
        Validate and assign the title of the place.

        Args:
            value (str): Title of the place.

        Raises:
            ValueError: If the title is empty.
            TypeError: If the title is not a string.
        """
        if not value:
            raise ValueError("Title cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        super().is_max_length('Title', value, 100)
        return value

    @validates("price")
    def validate_price(self, key, value):
        """
        Validate and assign the price of the place.

        Args:
            value (float | int): Price per night.

        Raises:
            TypeError: If the price is not numeric.
            ValueError: If the price is negative.
        """
        if not isinstance(value, (float, int)) or type(value) is bool:
            raise TypeError("Price must be a float")
        if value < 0:
            raise ValueError("Price must be positive.")
        return float(value)

    @validates("latitude")
    def validate_latitude(self, key, value):
        """
        Validate and assign the latitude of the place.

        Args:
            value (float | int): Latitude coordinate.

        Raises:
            TypeError: If the latitude is not numeric.
            ValueError: If the latitude is outside the range [-90, 90].
        """
        if not isinstance(value, (float, int)) or type(value) is bool:
            raise TypeError("Latitude must be a float")
        super().is_between("Latitude", value, -90, 90)
        return float(value)

    @validates("longitude")
    def validate_longitude(self, key, value):
        """
        Validate and assign the longitude of the place.

        Args:
            value (float | int): Longitude coordinate.

        Raises:
            TypeError: If the longitude is not numeric.
            ValueError: If the longitude is outside the range [-180, 180].
        """
        if not isinstance(value, (float, int)) or type(value) is bool:
            raise TypeError("Longitude must be a float")
        super().is_between("Longitude", value, -180, 180)
        return float(value)

    @validates("description")
    def validate_description(self, key, value):
        """
        Validate and assign the description of the place.

        Args:
            value (str | None): Optional description text.

        Raises:
            TypeError: If the description is not a string.
            ValueError: If the description exceeds the maximum length.
        """
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("Description must be a string")
            super().is_max_length('Description', value, 1024)
        return value

    def to_dict(self):
        """
        Serialize the Place object into a dictionary.

        This representation is typically used for API responses
        or JSON serialization.

        Returns:
            dict: A dictionary containing the place attributes.
        """
        owner = None
        if self.user is not None:
            owner = {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email
            }

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.user_id,
            'owner': owner,
            'amenities': [amenity.to_dict() for amenity in self.amenities]
        }
