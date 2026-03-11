from app import db, bcrypt
from app.models.basemodel import BaseModel
from sqlalchemy.orm import validates
import re


class User(BaseModel):
    """
    SQLAlchemy model representing a user in the HBnB application.

    This model defines the core attributes of a user, including personal
    information, authentication credentials, and administrative privileges.

    The class inherits from BaseModel, which provides common attributes
    and functionality such as:
        - id (UUID primary key)
        - created_at timestamp
        - updated_at timestamp
        - validation helpers (e.g. is_max_length, is_between)

    Passwords are stored in a hashed format using Flask-Bcrypt to ensure
    secure authentication.

    Relationships with other entities (such as Place and Review) are
    intentionally not implemented at this stage and will be added in
    later tasks.
    """

    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """
        Initialize a User instance.

        The constructor validates and assigns user attributes using
        dedicated validation methods before hashing and storing the password.

        Args:
            first_name (str): User's first name. Must be a string with a
                              maximum length of 50 characters.
            last_name (str): User's last name. Must be a string with a
                             maximum length of 50 characters.
            email (str): User's email address. Must follow a valid
                         email format and be unique.
            password (str): Plain text password that will be hashed
                            before being stored.
            is_admin (bool, optional): Indicates whether the user has
                                       administrative privileges.
                                       Defaults to False.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.hash_password(password)

    @validates("first_name")
    def validate_first_name(self, key, value):
        """
        Validate and assign the user's first name.

        Args:
            value (str): First name of the user.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the value exceeds the maximum allowed length.
        """
        if not isinstance(value, str):
            raise TypeError("First name must be a string")
        super().is_max_length('First name', value, 50)
        return value

    @validates("last_name")
    def validate_last_name(self, key, value):
        """
        Validate and assign the user's last name.

        Args:
            value (str): Last name of the user.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the value exceeds the maximum allowed length.
        """
        if not isinstance(value, str):
            raise TypeError("Last name must be a string")
        super().is_max_length('Last name', value, 50)
        return value

    @validates("email")
    def validate_email(self, key, value):
        """
        Validate and assign the user's email address.

        Args:
            value (str): Email address of the user.

        Raises:
            TypeError: If the email is not a string.
            ValueError: If the email format is invalid.
        """
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @validates("is_admin")
    def validate_is_admin(self, key, value):
        """
        Validate and assign the administrative status of the user.

        Args:
            value (bool): Boolean indicating whether the user is an
                          administrator.

        Raises:
            TypeError: If the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise TypeError("Is Admin must be a boolean")
        return value

    def to_dict(self):
        """
        Serialize the User object into a dictionary.

        This representation is typically used for API responses or JSON
        serialization. Sensitive data such as the password is not included.

        Returns:
            dict: A dictionary containing the public user attributes.
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        }

    def hash_password(self, password):
        """
        Hash the user's password before storing it.

        Args:
            password (str): Plain text password.

        The password is hashed using Flask-Bcrypt and stored in the
        `password` attribute.
        """
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """
        Verify whether a provided password matches the stored hashed password.

        Args:
            password (str): Plain text password to verify.

        Returns:
            bool: True if the password matches the stored hash,
                  False otherwise.
        """
        return bcrypt.check_password_hash(self.password, password)
