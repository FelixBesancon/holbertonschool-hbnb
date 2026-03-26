from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    """
    Facade providing a unified interface to the HBnB business layer.

    This class acts as an intermediary between the API layer and the
    persistence layer. It centralizes all operations related to the
    application's core entities:
        - User
        - Place
        - Review
        - Amenity

    By encapsulating repository access and entity creation logic, the
    facade simplifies the API layer and promotes separation of concerns.
    """
    def __init__(self):
        """
        Initialize the facade and all repositories used by the application.
        """
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # USER
    def create_user(self, user_data):
        """
        Create and persist a new user.

        Args:
            user_data (dict): Dictionary containing the user data.

        Returns:
            User: The newly created and persisted user.
        """
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_users(self):
        """
        Retrieve all users.

        Returns:
            list: A list of all persisted users.
        """
        return self.user_repo.get_all()

    def get_user(self, user_id):
        """
        Retrieve a user by its unique identifier.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            User | None: The matching user if found, otherwise None.
        """
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """
        Retrieve a user by email address.

        Args:
            email (str): Email address of the user.

        Returns:
            User | None: The matching user if found, otherwise None.
        """
        return self.user_repo.get_user_by_email(email)

    def update_user(self, user_id, user_data):
        """
        Update an existing user.

        Args:
            user_id (str): Unique identifier of the user to update.
            user_data (dict): Dictionary containing updated user values.
        """
        self.user_repo.update(user_id, user_data)

    # AMENITY
    def create_amenity(self, amenity_data):
        """
        Create and persist a new amenity.

        Args:
            amenity_data (dict): Dictionary containing the amenity data.

        Returns:
            Amenity: The newly created and persisted amenity.
        """
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """
        Retrieve an amenity by its unique identifier.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            Amenity | None: The matching amenity if found, otherwise None.
        """
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """
        Retrieve all amenities.

        Returns:
            list: A list of all persisted amenities.
        """
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """
        Update an existing amenity.

        Args:
            amenity_id (str): Unique identifier of the amenity to update.
            amenity_data (dict): Dictionary containing updated values.
        """
        self.amenity_repo.update(amenity_id, amenity_data)

    # PLACE
    def create_place(self, place_data):
        """
        Create and persist a new place.

        The method validates that the referenced user exists and, if
        provided, that all linked amenities are valid.

        Args:
            place_data (dict): Dictionary containing the place data.

        Returns:
            Place: The newly created and persisted place.

        Raises:
            KeyError: If the referenced user or amenities do not exist.
        """
        user = self.user_repo.get_by_attribute('id', place_data['owner_id'])
        if not user:
            raise KeyError('Invalid input data')

        owner_id = place_data.pop('owner_id')
        amenities = place_data.pop('amenities', None)

        # Validate amenities before creation
        amenity_objects = []
        if amenities:
            for a in amenities:
                amenity = self.get_amenity(a['id'])
                if not amenity:
                    raise KeyError('Invalid input data')
                amenity_objects.append(amenity)

        place = Place(**place_data)
        place.user_id = owner_id  # assigner la FK directement

        # Link amenities through SQLAlchemy relations
        for amenity in amenity_objects:
            place.amenities.append(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """
        Retrieve a place by its unique identifier.

        Args:
            place_id (str): Unique identifier of the place.

        Returns:
            Place | None: The matching place if found, otherwise None.
        """
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """
        Retrieve all places.

        Returns:
            list: A list of all persisted places.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update an existing place.

        Args:
            place_id (str): Unique identifier of the place to update.
            place_data (dict): Dictionary containing updated values.
        """
        self.place_repo.update(place_id, place_data)

    # REVIEWS
    def create_review(self, review_data):
        """
        Create and persist a new review.

        The method validates that the referenced user and place exist
        before creating the review.

        Args:
            review_data (dict): Dictionary containing the review data.

        Returns:
            Review: The newly created and persisted review.

        Raises:
            KeyError: If the referenced user or place do not exist.
        """
        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise KeyError('Invalid input data')

        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise KeyError('Invalid input data')

        review = Review(
            text=review_data['text'],
            rating=review_data['rating']
        )
        review.user_id = review_data['user_id']  # assigner les FKs directement
        review.place_id = review_data['place_id']

        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """
        Retrieve a review by its unique identifier.

        Args:
            review_id (str): Unique identifier of the review.

        Returns:
            Review | None: The matching review if found, otherwise None.
        """
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """
        Retrieve all reviews.

        Returns:
            list: A list of all persisted reviews.
        """
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Retrieve all reviews associated with a specific place.

        Args:
            place_id (str): Unique identifier of the place.

        Returns:
            list: A list of reviews linked to the given place.

        Raises:
            KeyError: If the place does not exist.
        """
        place = self.place_repo.get(place_id)
        if not place:
            raise KeyError('Place not found')
        return place.reviews

    def update_review(self, review_id, review_data):
        """
        Update an existing review.

        Args:
            review_id (str): Unique identifier of the review to update.
            review_data (dict): Dictionary containing updated values.
        """
        self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        """
        Delete an existing review from the database.

        Args:
            review_id (str): Unique identifier of the review to delete.
        """
        self.review_repo.delete(review_id)
