#!/usr/bin/python3
"""
Unit tests for Amenity endpoints.

Tests cover:
- Amenity creation (success and failure cases)
- Amenity retrieval by ID and list
- Amenity update (success and failure cases)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../hbnb')))

import unittest
from app import create_app


class TestAmenityEndpoints(unittest.TestCase):
    """Test suite for /api/v1/amenities/ endpoints."""

    def setUp(self):
        """Create a fresh app and test client before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        from app.services import facade
        facade.amenity_repo._storage.clear()

    # ----------------------------------------------------------------
    # POST /api/v1/amenities/  —  creation
    # ----------------------------------------------------------------
    def test_create_amenity_success(self):
        """Create a valid amenity → 201 with correct data."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Wi-Fi")

    def test_create_amenity_missing_name(self):
        """Missing name field → 400."""
        response = self.client.post('/api/v1/amenities/', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_empty_name(self):
        """Empty name → 400."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": ""
        })
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_name_too_long(self):
        """Name longer than 50 characters → 400."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": "A" * 51
        })
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_name_whitespace_only(self):
        """Name with only whitespace → 400."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": "   "
        })
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_name_is_number(self):
        """Name as integer instead of string → 400."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": 123
        })
        self.assertEqual(response.status_code, 400)

    # ----------------------------------------------------------------
    # GET /api/v1/amenities/  —  list
    # ----------------------------------------------------------------
    def test_get_amenities_empty(self):
        """Empty list on startup → 200 with empty list."""
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_amenities_after_creation(self):
        """After creating two amenities, the list contains exactly 2 items."""
        self.client.post('/api/v1/amenities/', json={"name": "Wi-Fi"})
        self.client.post('/api/v1/amenities/', json={"name": "Pool"})
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    # ----------------------------------------------------------------
    # GET /api/v1/amenities/<id>  —  retrieval by ID
    # ----------------------------------------------------------------
    def test_get_amenity_by_id_success(self):
        """Retrieve an existing amenity by ID → 200."""
        created = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        response = self.client.get(f'/api/v1/amenities/{created["id"]}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], created["id"])
        self.assertEqual(data["name"], "Wi-Fi")

    def test_get_amenity_not_found(self):
        """Non-existent ID → 404."""
        response = self.client.get(
            '/api/v1/amenities/00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # PUT /api/v1/amenities/<id>  —  update
    # ----------------------------------------------------------------
    def test_update_amenity_success(self):
        """Update amenity name → 200 with success message."""
        created = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        response = self.client.put(
            f'/api/v1/amenities/{created["id"]}',
            json={"name": "WiFi 6"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            "Amenity updated successfully"
        )

    def test_update_amenity_empty_name(self):
        """Update with empty name → 400."""
        created = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        response = self.client.put(
            f'/api/v1/amenities/{created["id"]}',
            json={"name": ""}
        )
        self.assertEqual(response.status_code, 400)

    def test_update_amenity_name_too_long(self):
        """Update with name longer than 50 characters → 400."""
        created = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        response = self.client.put(
            f'/api/v1/amenities/{created["id"]}',
            json={"name": "A" * 51}
        )
        self.assertEqual(response.status_code, 400)

    def test_update_amenity_not_found(self):
        """Update a non-existent amenity → 404."""
        response = self.client.put(
            '/api/v1/amenities/00000000-0000-0000-0000-000000000000',
            json={"name": "Ghost"}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_amenity_change_is_reflected(self):
        """After update, GET returns the new name."""
        created = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        }).get_json()
        self.client.put(
            f'/api/v1/amenities/{created["id"]}',
            json={"name": "Fiber Optic"}
        )
        response = self.client.get(f'/api/v1/amenities/{created["id"]}')
        self.assertEqual(response.get_json()["name"], "Fiber Optic")


if __name__ == '__main__':
    unittest.main()