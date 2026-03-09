#!/usr/bin/python3
"""
Unit tests for Review endpoints.

Tests cover:
- Review creation (success and failure cases)
- Review retrieval by ID and list
- Review update (success and failure cases)
- Review deletion
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../hbnb')))

import unittest
from app import create_app


class TestReviewEndpoints(unittest.TestCase):
    """Test suite for /api/v1/reviews/ endpoints."""

    def setUp(self):
        """Create a fresh app, test client, and valid user + place before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        from app.services import facade
        facade.user_repo._storage.clear()
        facade.place_repo._storage.clear()
        facade.amenity_repo._storage.clear()
        facade.review_repo._storage.clear()

        # Create owner
        owner = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        self.owner_id = owner["id"]

        # Create reviewer (different from owner)
        reviewer = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com"
        }).get_json()
        self.reviewer_id = reviewer["id"]

        # Create a place
        place = self.client.post('/api/v1/places/', json={
            "title": "Cozy Apartment",
            "description": "A nice place",
            "price": 80.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.owner_id,
            "amenities": []
        }).get_json()
        self.place_id = place["id"]

    def _create_review(self, **kwargs):
        """Helper to create a default valid review."""
        data = {
            "text": "Great place!",
            "rating": 5,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        }
        data.update(kwargs)
        return self.client.post('/api/v1/reviews/', json=data)

    # ----------------------------------------------------------------
    # POST /api/v1/reviews/  —  creation
    # ----------------------------------------------------------------
    def test_create_review_success(self):
        """Create a valid review → 201 with correct data."""
        response = self._create_review()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["text"], "Great place!")
        self.assertEqual(data["rating"], 5)
        self.assertEqual(data["user_id"], self.reviewer_id)
        self.assertEqual(data["place_id"], self.place_id)

    def test_create_review_minimum_rating(self):
        """Create a review with minimum rating (1) → 201."""
        response = self._create_review(rating=1)
        self.assertEqual(response.status_code, 201)

    def test_create_review_missing_text(self):
        """Missing text field → 400."""
        response = self.client.post('/api/v1/reviews/', json={
            "rating": 5,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_review_empty_text(self):
        """Empty text → 400."""
        response = self._create_review(text="")
        self.assertEqual(response.status_code, 400)

    def test_create_review_missing_rating(self):
        """Missing rating field → 400."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Great place!",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_review_rating_too_high(self):
        """Rating above 5 → 400."""
        response = self._create_review(rating=6)
        self.assertEqual(response.status_code, 400)

    def test_create_review_rating_too_low(self):
        """Rating below 1 → 400."""
        response = self._create_review(rating=0)
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_user_id(self):
        """Non-existent user_id → 400."""
        response = self._create_review(
            user_id="00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_place_id(self):
        """Non-existent place_id → 400."""
        response = self._create_review(
            place_id="00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_missing_user_id(self):
        """Missing user_id field → 400."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Great place!",
            "rating": 5,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_review_missing_place_id(self):
        """Missing place_id field → 400."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Great place!",
            "rating": 5,
            "user_id": self.reviewer_id
        })
        self.assertEqual(response.status_code, 400)

    # ----------------------------------------------------------------
    # GET /api/v1/reviews/  —  list
    # ----------------------------------------------------------------
    def test_get_reviews_empty(self):
        """Empty list on startup → 200 with empty list."""
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_reviews_after_creation(self):
        """After creating two reviews, the list contains exactly 2 items."""
        self._create_review(text="First review")

        # Create a second reviewer to avoid duplicates
        reviewer2 = self.client.post('/api/v1/users/', json={
            "first_name": "Bob",
            "last_name": "Brown",
            "email": "bob.brown@example.com"
        }).get_json()
        self._create_review(text="Second review", user_id=reviewer2["id"])

        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    # ----------------------------------------------------------------
    # GET /api/v1/reviews/<id>  —  retrieval by ID
    # ----------------------------------------------------------------
    def test_get_review_by_id_success(self):
        """Retrieve an existing review by ID → 200."""
        created = self._create_review().get_json()
        response = self.client.get(f'/api/v1/reviews/{created["id"]}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], created["id"])
        self.assertEqual(data["text"], "Great place!")
        self.assertEqual(data["rating"], 5)

    def test_get_review_not_found(self):
        """Non-existent ID → 404."""
        response = self.client.get(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # PUT /api/v1/reviews/<id>  —  update
    # ----------------------------------------------------------------
    def test_update_review_success(self):
        """Update review text and rating → 200 with success message."""
        created = self._create_review().get_json()
        response = self.client.put(f'/api/v1/reviews/{created["id"]}', json={
            "text": "Updated review",
            "rating": 4,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            "Review updated successfully"
        )

    def test_update_review_change_is_reflected(self):
        """After update, GET returns the new values."""
        created = self._create_review().get_json()
        self.client.put(f'/api/v1/reviews/{created["id"]}', json={
            "text": "Actually just okay",
            "rating": 3,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        response = self.client.get(f'/api/v1/reviews/{created["id"]}')
        data = response.get_json()
        self.assertEqual(data["text"], "Actually just okay")
        self.assertEqual(data["rating"], 3)

    def test_update_review_rating_too_high(self):
        """Update with rating above 5 → 400."""
        created = self._create_review().get_json()
        response = self.client.put(f'/api/v1/reviews/{created["id"]}', json={
            "text": "Great!",
            "rating": 6,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_update_review_empty_text(self):
        """Update with empty text → 400."""
        created = self._create_review().get_json()
        response = self.client.put(f'/api/v1/reviews/{created["id"]}', json={
            "text": "",
            "rating": 4,
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_update_review_not_found(self):
        """Update a non-existent review → 404."""
        response = self.client.put(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000',
            json={
                "text": "Ghost",
                "rating": 3,
                "user_id": self.reviewer_id,
                "place_id": self.place_id
            }
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # DELETE /api/v1/reviews/<id>  —  deletion
    # ----------------------------------------------------------------
    def test_delete_review_success(self):
        """Delete an existing review → 200 with success message."""
        created = self._create_review().get_json()
        response = self.client.delete(f'/api/v1/reviews/{created["id"]}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            "Review deleted successfully"
        )

    def test_delete_review_no_longer_exists(self):
        """After deletion, GET on the review → 404."""
        created = self._create_review().get_json()
        self.client.delete(f'/api/v1/reviews/{created["id"]}')
        response = self.client.get(f'/api/v1/reviews/{created["id"]}')
        self.assertEqual(response.status_code, 404)

    def test_delete_review_not_found(self):
        """Delete a non-existent review → 404."""
        response = self.client.delete(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()