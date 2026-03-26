from app.models.user import User
from app import db
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """
    Specialized repository for the User entity.

    This repository extends the generic SQLAlchemyRepository by adding
    user-specific query methods. It centralizes all persistence logic
    related to the User model.

    The UserRepository is particularly useful for authentication and
    account management use cases, such as retrieving a user by email.
    """
    def __init__(self):
        """
        Initialize the repository with the User model.
        """
        super().__init__(User)

    def get_user_by_email(self, email):
        """
        Retrieve a user by email address.

        Args:
            email (str): Email address of the user to retrieve.

        Returns:
            User | None: The matching user if found, otherwise None.
        """
        return self.model.query.filter_by(email=email).first()
