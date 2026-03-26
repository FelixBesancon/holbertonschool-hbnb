from app import db
from app.models.basemodel import BaseModel
from sqlalchemy.orm import validates


class Review(BaseModel):
    """
    SQLAlchemy model representing a review in the HBnB application.

    This model defines the core attributes of a review, including its text
    content and rating.

    The class inherits from BaseModel, which provides common attributes
    and functionality such as:
        - id (UUID primary key)
        - created_at timestamp
        - updated_at timestamp
        - validation helpers (e.g. is_max_length, is_between)

    Relationships with other entities (User, Place) are intentionally
    not implemented at this stage and will be added in later tasks.
    """

    __tablename__ = 'reviews'

    text = db.Column(db.String(1024), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id'),
        nullable=False
        )
    place_id = db.Column(
        db.String(36),
        db.ForeignKey('places.id'),
        nullable=False
        )

    def __init__(self, text, rating):
        """
        Initialize a Review instance.

        Args:
            text (str): Review content. Must be a non-empty string with
                        a maximum length of 1024 characters.
            rating (int): Review rating. Must be an integer between 1 and 5.
        """
        self.text = text
        self.rating = rating

    @validates("text")
    def validate_text(self, key, value):
        """
        Validate and assign the review text.

        Args:
            value (str): Review content.

        Raises:
            ValueError: If the text is empty.
            TypeError: If the text is not a string.
        """
        if not value:
            raise ValueError("Text cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Text must be a string")
        super().is_max_length('Text', value, 1024)
        return value

    @validates("rating")
    def validate_rating(self, key, value):
        """
        Validate and assign the review rating.

        Args:
            value (int): Rating value.

        Raises:
            TypeError: If the rating is not an integer.
            ValueError: If the rating is not between 1 and 5.
        """
        if not isinstance(value, int) or type(value) is bool:
            raise TypeError("Rating must be an integer")
        super().is_between('Rating', value, 1, 5)
        return value

    def to_dict(self):
        """
        Serialize the Review object into a dictionary.

        Returns:
            dict: A dictionary containing the review attributes.
        """
        return {
            'id': self.id,
            'text': self.text,
            'rating': self.rating,
        }
