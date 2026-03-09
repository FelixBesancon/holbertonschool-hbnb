#!/usr/bin/python3
"""
Facade module.

Provides the HBnBFacade class, which acts as the single entry point
between the Presentation layer (API) and the application's core logic
and persistence mechanisms.
"""


from app.persistence.repository import InMemoryRepository
from app.models.user import User, re
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review


class HBnBFacade:
    """
    Central access point for all business logic operations.

    This class coordinates interactions between:
    - The API layer (Flask-RESTx)
    - The domain models (User, Place, Review, Amenity)
    - The persistence layer (repositories)

    It ensures separation of concerns and encapsulates validation
    and repository interactions.
    """
    def __init__(self):
        """
        Initialize in-memory repositories for each entity.

        Each entity type is managed by its own repository instance.
        """
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ------------------------------------------------------------
    # -------------------------- USERS ---------------------------
    # ------------------------------------------------------------
    def create_user(self, user_data):
        """
        Create and store a new user.

        Args:
            user_data (dict): Dictionary containing user attributes.

        Returns:
            User: The created user instance.
        """
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """
        Retrieve a user by ID.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return self.user_repo.get(user_id)

    def get_users(self):
        """
        Retrieve all users.

        Returns:
            list[User]: List of all stored users.
        """
        return self.user_repo.get_all()

    def get_user_by_email(self, email):
        """
        Retrieve a user by email address.

        Args:
            email (str): The email to search for.

        Returns:
            User | None: The matching user if found.
        """
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id, user_data):
        """
        Update an existing user.

        Protected fields (id, timestamps, admin status, relationships)
        cannot be modified.

        Args:
            user_id (str): The user ID.
            user_data (dict): Fields to update.

        Returns:
            User | None: Updated user if found, otherwise None.
        """
        user = self.user_repo.get(user_id)
        if not user:
            return None

        # prevent protected fields from being updated
        forbidden = {
            'id', 'created_at', 'updated_at',
            'is_admin', 'place_ids', 'review_ids'
            }
        clean_data = {k: v for k, v in user_data.items() if k not in forbidden}

        # ---- first_name ----
        if 'first_name' in clean_data:
            first_name = clean_data['first_name']
            if not isinstance(first_name, str):
                raise TypeError("first_name must be a string")
            first_name = first_name.strip()
            if first_name == "":
                raise ValueError("first_name cannot be empty")
            clean_data['first_name'] = first_name

        # ---- last_name ----
        if 'last_name' in clean_data:
            last_name = clean_data['last_name']
            if not isinstance(last_name, str):
                raise TypeError("last_name must be a string")
            last_name = last_name.strip()
            if last_name == "":
                raise ValueError("last_name cannot be empty")
            clean_data['last_name'] = last_name

        # ---- email ----
        if 'email' in clean_data:
            email = clean_data['email']
            if not isinstance(email, str):
                raise TypeError("email must be a string")
            email = email.strip().lower()
            if email == "":
                raise ValueError("email cannot be empty")

            # Simple email format check (enough for the project)
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                raise ValueError("Invalid email format")

            clean_data['email'] = email
        self.user_repo.update(user_id, clean_data)
        return self.user_repo.get(user_id)

    # ------------------------------------------------------------
    # -------------------------- PLACES --------------------------
    # ------------------------------------------------------------
    def create_place(self, place_data):
        """
        Create and store a new place.

        Args:
            place_data (dict): Dictionary containing place attributes.

        Raises:
            ValueError: If the owner does not exist.

        Returns:
            Place: The created place instance.
        """
        if not self.user_repo.get(place_data["owner_id"]):
            raise ValueError("Owner not found")
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """
        Retrieve a place by ID.

        Args:
            place_id (str): The place's unique identifier.

        Returns:
            Place | None: The place if found.
        """
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """
        Retrieve all places.

        Returns:
            list[Place]: List of all stored places.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update an existing place.

        Protected fields (id, timestamps, owner_id) cannot be modified.

        Args:
            place_id (str): The place ID.
            place_data (dict): Fields to update.

        Returns:
            Place | None: Updated place if found, otherwise None.
        """
        place = self.place_repo.get(place_id)
        if not place:
            return None

        # Handle amenity_ids separately via the model's helper
        if 'amenities' in place_data and place_data['amenities'] is not None:
            if not isinstance(place_data['amenities'], list):
                raise TypeError("amenities must be a list of UUID strings")
            place.amenity_ids = []
            for aid in place_data['amenities']:
                place.add_amenity_id(aid)

        # prevent protected fields from being updated
        forbidden = {'id', 'created_at', 'updated_at', 'owner_id'}
        clean_data = {
            k: v for k, v in place_data.items() if k not in forbidden
            }

        # Re-validate updated fields (only if provided)
        if 'title' in clean_data:
            title = clean_data['title']
            if not isinstance(title, str):
                raise TypeError("Title must be a string")
            title = title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            if len(title) > 100:
                raise ValueError("Title must be <= 100 characters")
            clean_data['title'] = title

        if 'description' in clean_data:
            description = clean_data['description']
            if description is None:
                description = ""
            if not isinstance(description, str):
                raise TypeError("Description must be a string")
            clean_data['description'] = description.strip()

        if 'price' in clean_data:
            price = clean_data['price']
            if not isinstance(price, (int, float)) or type(price) is bool:
                raise TypeError("Price must be a number")
            if price <= 0:
                raise ValueError("Price must be positive")
            clean_data['price'] = float(price)

        if 'latitude' in clean_data:
            latitude = clean_data['latitude']
            if not isinstance(latitude, (int, float)) or type(latitude) is bool:
                raise TypeError("Latitude must be a number")
            if latitude < -90.0 or latitude > 90.0:
                raise ValueError("Latitude must be between -90 and 90")
            clean_data['latitude'] = float(latitude)

        if 'longitude' in clean_data:
            longitude = clean_data['longitude']
            if not isinstance(longitude, (int, float)) or type(longitude) is bool:
                raise TypeError("Longitude must be a number")
            if longitude < -180.0 or longitude > 180.0:
                raise ValueError("Longitude must be between -180 and 180")
            clean_data['longitude'] = float(longitude)

        self.place_repo.update(place_id, clean_data)
        return self.place_repo.get(place_id)
        

    # ------------------------------------------------------------
    # -------------------------- REVIEWS -------------------------
    # ------------------------------------------------------------
    def create_review(self, review_data):
        """
        Create and store a new review.

        Validates that:
        - The associated user exists
        - The associated place exists

        Args:
            review_data (dict): Dictionary containing review attributes.

        Raises:
            ValueError: If user or place does not exist.

        Returns:
            Review: The created review instance.
        """
        if not self.user_repo.get(review_data["user_id"]):
            raise ValueError("User not found")

        if not self.place_repo.get(review_data["place_id"]):
            raise ValueError("Place not found")

        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """
        Retrieve a review by ID.

        Args:
            review_id (str): Review unique identifier.

        Returns:
            Review | None
        """
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """
        Retrieve all reviews.

        Returns:
            list[Review]
        """
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Retrieve all reviews associated with a given place.

        Args:
            place_id (str): Place identifier.

        Returns:
            list[Review]
        """
        return [
            review
            for review in self.review_repo.get_all()
            if review.place_id == place_id
        ]

    def update_review(self, review_id, review_data):
        """
        Update an existing review.

        Protected fields (id, timestamps, user_id, place_id)
        cannot be modified.

        Args:
            review_id (str): Review ID.
            review_data (dict): Fields to update.

        Returns:
            Review | None
        """
        review = self.review_repo.get(review_id)
        if not review:
            return None

        # prevent protected fields from being updated
        forbidden = {
            'id', 'created_at', 'updated_at',
            'user_id', 'place_id'
            }
        clean_data = {
            k: v for k, v in review_data.items() if k not in forbidden
            }

        # ---- Validate text (if provided) ----
        if 'text' in clean_data:
            text = clean_data['text']
            if not isinstance(text, str):
                raise TypeError("Text must be a string")
            text = text.strip()
            if text == "":
                raise ValueError("Text cannot be empty")
            clean_data['text'] = text

        # ---- Validate rating (if provided) ----
        if 'rating' in clean_data:
            rating = clean_data['rating']
            if not isinstance(rating, int) or isinstance(rating, bool):
                raise TypeError("Rating must be an integer")
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            clean_data['rating'] = rating
            self.review_repo.update(review_id, clean_data)
            return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        """
        Delete a review by ID.

        Args:
            review_id (str): Review identifier.

        Returns:
            bool | None:
                True if deleted,
                None if review not found.
        """
        review = self.review_repo.get(review_id)
        if not review:
            return None

        self.review_repo.delete(review_id)
        return True

    # ------------------------------------------------------------
    # -------------------------- AMENITIES -----------------------
    # ------------------------------------------------------------
    def create_amenity(self, amenity_data):
        """
        Create and store a new amenity.

        Validation of name (type, length, empty) is delegated
        to the Amenity model.

        Args:
            amenity_data (dict): Dictionary containing amenity attributes.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is empty or exceeds 50 characters.

        Returns:
            Amenity: The created amenity instance.
        """
        if not isinstance(amenity_data, dict):
            raise TypeError("amenity_data must be a dictionary")

        if "name" not in amenity_data:
            raise ValueError("name is required")

        amenity = Amenity(amenity_data["name"])
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """
        Retrieve an amenity by ID.

        Args:
            amenity_id (str): The amenity's unique identifier.

        Returns:
            Amenity | None: The amenity if found, otherwise None.
        """
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """
        Retrieve all amenities.

        Returns:
            list[Amenity]: List of all stored amenities.
        """
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """
        Update an existing amenity.

        Protected fields (id, timestamps) cannot be modified.

        Args:
            amenity_id (str): The amenity ID.
            amenity_data (dict): Fields to update.

        Returns:
            Amenity | None: Updated amenity if found, otherwise None.
        """
        if not isinstance(amenity_data, dict):
            raise TypeError("amenity_data must be a dictionary")

        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None

        if "name" not in amenity_data:
            raise ValueError("name is required")
        
        name = amenity_data["name"]

        #revalidate the "name" format
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

        name = name.strip()

        if name == "":
            raise ValueError("Name cannot be empty")

        if len(name) > 50:
            raise ValueError("Name must be 50 characters maximum")

        # prevent protected fields from being updated
        forbidden = {'id', 'created_at', 'updated_at'}
        clean_data = {
            k: v for k, v in amenity_data.items() if k not in forbidden
            }

        self.amenity_repo.update(amenity_id, clean_data)
        return self.amenity_repo.get(amenity_id)
