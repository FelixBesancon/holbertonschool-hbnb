
#!/usr/bin/python3
"""
Integration tests for the HBnB API.

Tests a complete scenario:
- 1 owner user
- 1 reviewer user
- 2 amenities
- 2 places (owned by the same user, each with amenities)
- 2 reviews per place (written by the reviewer)

Verifies all relationships and interactions between entities.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../hbnb')))

import unittest
from app import create_app


class TestIntegration(unittest.TestCase):
    """
    Full integration test suite.

    Builds a complete object graph via the API and verifies
    that all relationships are correctly established and reflected
    in GET responses.
    """

    def setUp(self):
        """Create a fresh app and reset all repositories."""
        self.app = create_app()
        self.client = self.app.test_client()
        from app.services import facade
        facade.user_repo._storage.clear()
        facade.place_repo._storage.clear()
        facade.amenity_repo._storage.clear()
        facade.review_repo._storage.clear()

        # ---- Users ----
        self.owner = self.client.post('/api/v1/users/', json={
            "first_name": "Alice",
            "last_name": "Owner",
            "email": "alice.owner@example.com"
        }).get_json()

        self.reviewer = self.client.post('/api/v1/users/', json={
            "first_name": "Bob",
            "last_name": "Reviewer",
            "email": "bob.reviewer@example.com"
        }).get_json()

        # ---- Amenities ----
        self.amenity1 = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()

        self.amenity2 = self.client.post('/api/v1/amenities/', json={
            "name": "Pool"
        }).get_json()

        # ---- Places ----
        self.place1 = self.client.post('/api/v1/places/', json={
            "title": "Beach House",
            "description": "A house by the sea",
            "price": 150.0,
            "latitude": 43.70,
            "longitude": 7.27,
            "owner_id": self.owner["id"],
            "amenities": [self.amenity1["id"], self.amenity2["id"]]
        }).get_json()

        self.place2 = self.client.post('/api/v1/places/', json={
            "title": "Mountain Cabin",
            "description": "A cozy cabin in the mountains",
            "price": 90.0,
            "latitude": 45.18,
            "longitude": 5.72,
            "owner_id": self.owner["id"],
            "amenities": [self.amenity1["id"]]
        }).get_json()

        # ---- Reviews ----
        self.review1_place1 = self.client.post('/api/v1/reviews/', json={
            "text": "Absolutely loved the beach house!",
            "rating": 5,
            "user_id": self.reviewer["id"],
            "place_id": self.place1["id"]
        }).get_json()

        self.review2_place1 = self.client.post('/api/v1/reviews/', json={
            "text": "Great location but a bit noisy",
            "rating": 4,
            "user_id": self.reviewer["id"],
            "place_id": self.place1["id"]
        }).get_json()

        self.review1_place2 = self.client.post('/api/v1/reviews/', json={
            "text": "Perfect mountain retreat",
            "rating": 5,
            "user_id": self.reviewer["id"],
            "place_id": self.place2["id"]
        }).get_json()

        self.review2_place2 = self.client.post('/api/v1/reviews/', json={
            "text": "Nice but far from everything",
            "rating": 3,
            "user_id": self.reviewer["id"],
            "place_id": self.place2["id"]
        }).get_json()

    # ----------------------------------------------------------------
    # Verify all objects were created successfully
    # ----------------------------------------------------------------
    def test_all_objects_created(self):
        """All users, amenities, places and reviews are created successfully."""
        self.assertIn("id", self.owner)
        self.assertIn("id", self.reviewer)
        self.assertIn("id", self.amenity1)
        self.assertIn("id", self.amenity2)
        self.assertIn("id", self.place1)
        self.assertIn("id", self.place2)
        self.assertIn("id", self.review1_place1)
        self.assertIn("id", self.review2_place1)
        self.assertIn("id", self.review1_place2)
        self.assertIn("id", self.review2_place2)

    # ----------------------------------------------------------------
    # Users
    # ----------------------------------------------------------------
    def test_users_list_contains_both_users(self):
        """The users list contains exactly 2 users."""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(len(response.get_json()), 2)

    def test_owner_details_are_correct(self):
        """Owner details match what was submitted."""
        response = self.client.get(f'/api/v1/users/{self.owner["id"]}')
        data = response.get_json()
        self.assertEqual(data["first_name"], "Alice")
        self.assertEqual(data["email"], "alice.owner@example.com")

    # ----------------------------------------------------------------
    # Amenities
    # ----------------------------------------------------------------
    def test_amenities_list_contains_both(self):
        """The amenities list contains exactly 2 amenities."""
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(len(response.get_json()), 2)

    # ----------------------------------------------------------------
    # Places
    # ----------------------------------------------------------------
    def test_places_list_contains_both_places(self):
        """The places list contains exactly 2 places."""
        response = self.client.get('/api/v1/places/')
        self.assertEqual(len(response.get_json()), 2)

    def test_place1_owner_is_correct(self):
        """Place 1 owner matches the created owner."""
        response = self.client.get(f'/api/v1/places/{self.place1["id"]}')
        owner = response.get_json()["owner"]
        self.assertEqual(owner["id"], self.owner["id"])
        self.assertEqual(owner["first_name"], "Alice")

    def test_place1_has_two_amenities(self):
        """Place 1 has 2 amenities (Wi-Fi and Pool)."""
        response = self.client.get(f'/api/v1/places/{self.place1["id"]}')
        amenities = response.get_json()["amenities"]
        self.assertEqual(len(amenities), 2)
        amenity_names = [a["name"] for a in amenities]
        self.assertIn("Wi-Fi", amenity_names)
        self.assertIn("Pool", amenity_names)

    def test_place2_has_one_amenity(self):
        """Place 2 has 1 amenity (Wi-Fi only)."""
        response = self.client.get(f'/api/v1/places/{self.place2["id"]}')
        amenities = response.get_json()["amenities"]
        self.assertEqual(len(amenities), 1)
        self.assertEqual(amenities[0]["name"], "Wi-Fi")

    def test_place1_has_two_reviews(self):
        """Place 1 has 2 reviews."""
        response = self.client.get(
            f'/api/v1/places/{self.place1["id"]}/reviews'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_place2_has_two_reviews(self):
        """Place 2 has 2 reviews."""
        response = self.client.get(
            f'/api/v1/places/{self.place2["id"]}/reviews'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_place1_reviews_belong_to_correct_place(self):
        """All reviews for place 1 have place_id matching place 1."""
        response = self.client.get(
            f'/api/v1/places/{self.place1["id"]}/reviews'
        )
        for review in response.get_json():
            self.assertEqual(review["place_id"], self.place1["id"])

    def test_place2_reviews_belong_to_correct_place(self):
        """All reviews for place 2 have place_id matching place 2."""
        response = self.client.get(
            f'/api/v1/places/{self.place2["id"]}/reviews'
        )
        for review in response.get_json():
            self.assertEqual(review["place_id"], self.place2["id"])

    # ----------------------------------------------------------------
    # Reviews
    # ----------------------------------------------------------------
    def test_reviews_list_contains_all_four(self):
        """The reviews list contains exactly 4 reviews."""
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(len(response.get_json()), 4)

    def test_review_details_are_correct(self):
        """Review 1 for place 1 has correct text, rating, user and place."""
        response = self.client.get(
            f'/api/v1/reviews/{self.review1_place1["id"]}'
        )
        data = response.get_json()
        self.assertEqual(data["text"], "Absolutely loved the beach house!")
        self.assertEqual(data["rating"], 5)
        self.assertEqual(data["user_id"], self.reviewer["id"])
        self.assertEqual(data["place_id"], self.place1["id"])

    # ----------------------------------------------------------------
    # Update interactions
    # ----------------------------------------------------------------
    def test_update_place_price_reflected_in_get(self):
        """After updating place price, GET returns the new price."""
        self.client.put(f'/api/v1/places/{self.place1["id"]}', json={
            "price": 200.0
        })
        response = self.client.get(f'/api/v1/places/{self.place1["id"]}')
        self.assertEqual(response.get_json()["price"], 200.0)

    def test_update_review_rating_reflected_in_get(self):
        """After updating review rating, GET returns the new rating."""
        self.client.put(f'/api/v1/reviews/{self.review1_place1["id"]}', json={
            "text": "Absolutely loved the beach house!",
            "rating": 4,
            "user_id": self.reviewer["id"],
            "place_id": self.place1["id"]
        })
        response = self.client.get(
            f'/api/v1/reviews/{self.review1_place1["id"]}'
        )
        self.assertEqual(response.get_json()["rating"], 4)

    def test_update_amenity_name_reflected_in_place(self):
        """After updating amenity name, GET place shows the updated name."""
        self.client.put(f'/api/v1/amenities/{self.amenity1["id"]}', json={
            "name": "Fiber Optic"
        })
        response = self.client.get(f'/api/v1/places/{self.place1["id"]}')
        amenity_names = [
            a["name"] for a in response.get_json()["amenities"]
        ]
        self.assertIn("Fiber Optic", amenity_names)

    # ----------------------------------------------------------------
    # Delete interactions
    # ----------------------------------------------------------------
    def test_delete_review_reduces_list(self):
        """After deleting one review, the global list has 3 reviews."""
        self.client.delete(f'/api/v1/reviews/{self.review1_place1["id"]}')
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(len(response.get_json()), 3)

    def test_delete_review_reduces_place_reviews(self):
        """After deleting one review for place 1, place 1 has only 1 review."""
        self.client.delete(f'/api/v1/reviews/{self.review1_place1["id"]}')
        response = self.client.get(
            f'/api/v1/places/{self.place1["id"]}/reviews'
        )
        self.assertEqual(len(response.get_json()), 1)

    def test_deleted_review_not_accessible(self):
        """Deleted review returns 404 on GET."""
        self.client.delete(f'/api/v1/reviews/{self.review1_place1["id"]}')
        response = self.client.get(
            f'/api/v1/reviews/{self.review1_place1["id"]}'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()