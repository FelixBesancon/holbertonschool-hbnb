#!/usr/bin/python3
"""
Unit tests for Place endpoints.

Tests cover:
- Place creation (success and failure cases)
- Place retrieval by ID and list
- Place update (success and failure cases)
- Reviews list for a place
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../hbnb')))

import unittest
from app import create_app


class TestPlaceEndpoints(unittest.TestCase):
    """Test suite for /api/v1/places/ endpoints."""

    def setUp(self):
        """Create a fresh app, test client, and a valid user before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        from app.services import facade
        facade.user_repo._storage.clear()
        facade.place_repo._storage.clear()
        facade.amenity_repo._storage.clear()
        facade.review_repo._storage.clear()

        # Create a user to use as owner in place tests
        user = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        self.user_id = user["id"]

        # Create an amenity to use in place tests
        amenity = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        self.amenity_id = amenity["id"]

    def _create_place(self, **kwargs):
        """Helper to create a default valid place."""
        data = {
            "title": "Cozy Apartment",
            "description": "A nice place",
            "price": 80.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        data.update(kwargs)
        return self.client.post('/api/v1/places/', json=data)

    # ----------------------------------------------------------------
    # POST /api/v1/places/  —  creation
    # ----------------------------------------------------------------
    def test_create_place_success(self):
        """Create a valid place → 201 with correct data."""
        response = self._create_place()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Cozy Apartment")
        self.assertEqual(data["price"], 80.0)
        self.assertEqual(data["owner_id"], self.user_id)

    def test_create_place_with_amenities(self):
        """Create a place with amenities → 201."""
        response = self._create_place(amenities=[self.amenity_id])
        self.assertEqual(response.status_code, 201)

    def test_create_place_missing_title(self):
        """Missing title → 400."""
        response = self.client.post('/api/v1/places/', json={
            "price": 80.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        })
        self.assertEqual(response.status_code, 400)

    def test_create_place_empty_title(self):
        """Empty title → 400."""
        response = self._create_place(title="")
        self.assertEqual(response.status_code, 400)

    def test_create_place_title_too_long(self):
        """Title longer than 100 characters → 400."""
        response = self._create_place(title="T" * 101)
        self.assertEqual(response.status_code, 400)

    def test_create_place_negative_price(self):
        """Negative price → 400."""
        response = self._create_place(price=-10.0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_zero_price(self):
        """Price of 0 → 400."""
        response = self._create_place(price=0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_latitude_too_high(self):
        """Latitude above 90 → 400."""
        response = self._create_place(latitude=91.0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_latitude_too_low(self):
        """Latitude below -90 → 400."""
        response = self._create_place(latitude=-91.0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_longitude_too_high(self):
        """Longitude above 180 → 400."""
        response = self._create_place(longitude=181.0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_longitude_too_low(self):
        """Longitude below -180 → 400."""
        response = self._create_place(longitude=-181.0)
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_owner(self):
        """Non-existent owner_id → 400."""
        response = self._create_place(
            owner_id="00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_missing_owner_id(self):
        """Missing owner_id → 400."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Cozy Apartment",
            "price": 80.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "amenities": []
        })
        self.assertEqual(response.status_code, 400)

    # ----------------------------------------------------------------
    # GET /api/v1/places/  —  list
    # ----------------------------------------------------------------
    def test_get_places_empty(self):
        """Empty list on startup → 200 with empty list."""
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_places_after_creation(self):
        """After creating two places, the list contains exactly 2 items."""
        self._create_place(title="Place 1")
        self._create_place(title="Place 2")
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_get_places_list_format(self):
        """List endpoint returns id, title, latitude, longitude only."""
        self._create_place()
        response = self.client.get('/api/v1/places/')
        data = response.get_json()[0]
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)
        self.assertNotIn("description", data)
        self.assertNotIn("owner_id", data)

    # ----------------------------------------------------------------
    # GET /api/v1/places/<id>  —  retrieval by ID
    # ----------------------------------------------------------------
    def test_get_place_by_id_success(self):
        """Retrieve an existing place by ID → 200 with full details."""
        created = self._create_place().get_json()
        response = self.client.get(f'/api/v1/places/{created["id"]}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("owner", data)
        self.assertIn("amenities", data)
        self.assertIn("reviews", data)

    def test_get_place_by_id_owner_details(self):
        """GET place by ID includes full owner details."""
        created = self._create_place().get_json()
        response = self.client.get(f'/api/v1/places/{created["id"]}')
        owner = response.get_json()["owner"]
        self.assertEqual(owner["id"], self.user_id)
        self.assertEqual(owner["first_name"], "John")

    def test_get_place_not_found(self):
        """Non-existent ID → 404."""
        response = self.client.get(
            '/api/v1/places/00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # PUT /api/v1/places/<id>  —  update
    # ----------------------------------------------------------------
    def test_update_place_success(self):
        """Update place title and price → 200 with success message."""
        created = self._create_place().get_json()
        response = self.client.put(f'/api/v1/places/{created["id"]}', json={
            "title": "Updated Title",
            "price": 120.0
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            "Place updated successfully"
        )

    def test_update_place_change_is_reflected(self):
        """After update, GET returns the new values."""
        created = self._create_place().get_json()
        self.client.put(f'/api/v1/places/{created["id"]}', json={
            "title": "New Title",
            "price": 150.0
        })
        response = self.client.get(f'/api/v1/places/{created["id"]}')
        data = response.get_json()
        self.assertEqual(data["title"], "New Title")
        self.assertEqual(data["price"], 150.0)

    def test_update_place_negative_price(self):
        """Update with negative price → 400."""
        created = self._create_place().get_json()
        response = self.client.put(f'/api/v1/places/{created["id"]}', json={
            "price": -50.0
        })
        self.assertEqual(response.status_code, 400)

    def test_update_place_latitude_out_of_range(self):
        """Update with latitude out of range → 400."""
        created = self._create_place().get_json()
        response = self.client.put(f'/api/v1/places/{created["id"]}', json={
            "latitude": 95.0
        })
        self.assertEqual(response.status_code, 400)

    def test_update_place_longitude_out_of_range(self):
        """Update with longitude out of range → 400."""
        created = self._create_place().get_json()
        response = self.client.put(f'/api/v1/places/{created["id"]}', json={
            "longitude": -200.0
        })
        self.assertEqual(response.status_code, 400)

    def test_update_place_owner_id_is_forbidden(self):
        """Attempting to modify owner_id → owner_id remains unchanged."""
        created = self._create_place().get_json()
        self.client.put(f'/api/v1/places/{created["id"]}', json={
            "owner_id": "00000000-0000-0000-0000-000000000000",
            "title": "New Title"
        })
        response = self.client.get(f'/api/v1/places/{created["id"]}')
        self.assertEqual(
            response.get_json()["owner"]["id"],
            self.user_id
        )

    def test_update_place_not_found(self):
        """Update a non-existent place → 404."""
        response = self.client.put(
            '/api/v1/places/00000000-0000-0000-0000-000000000000',
            json={"title": "Ghost"}
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # GET /api/v1/places/<id>/reviews  —  reviews for a place
    # ----------------------------------------------------------------
    def test_get_reviews_for_place_empty(self):
        """No reviews yet for a place → 200 with empty list."""
        created = self._create_place().get_json()
        response = self.client.get(
            f'/api/v1/places/{created["id"]}/reviews'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_reviews_for_nonexistent_place(self):
        """Reviews for non-existent place → 404."""
        response = self.client.get(
            '/api/v1/places/00000000-0000-0000-0000-000000000000/reviews'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()