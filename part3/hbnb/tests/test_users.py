#!/usr/bin/python3
"""
Unit tests for User endpoints.

Tests cover:
- User creation (success and failure cases)
- User retrieval by ID and list
- User update (success and forbidden fields)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../hbnb')))

import unittest
from app import create_app


class TestUserEndpoints(unittest.TestCase):
    """Test suite for /api/v1/users/ endpoints."""

    def setUp(self):
        """Create a fresh app and test client before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        from app.services import facade
        facade.user_repo._storage.clear()

    # ----------------------------------------------------------------
    # POST /api/v1/users/  —  creation
    # ----------------------------------------------------------------
    def test_create_user_success(self):
        """Create a valid user → 201 with correct data."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["email"], "john.doe@example.com")

    def test_create_user_missing_first_name(self):
        """Missing first_name field → 400."""
        response = self.client.post('/api/v1/users/', json={
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_missing_last_name(self):
        """Missing last_name field → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_missing_email(self):
        """Missing email field → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_empty_first_name(self):
        """Empty first_name → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_empty_last_name(self):
        """Empty last_name → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_first_name_too_long(self):
        """first_name longer than 50 characters → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "J" * 51,
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_last_name_too_long(self):
        """last_name longer than 50 characters → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "D" * 51,
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email_no_at(self):
        """Email without @ sign → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "not-an-email"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email_no_domain(self):
        """Email without domain → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email_no_tld(self):
        """Email without TLD → 400."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_email(self):
        """Two users with the same email → 409 on the second request."""
        self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "duplicate@example.com"
        })
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "duplicate@example.com"
        })
        self.assertEqual(response.status_code, 409)
        self.assertIn("error", response.get_json())

    # ----------------------------------------------------------------
    # GET /api/v1/users/  —  list
    # ----------------------------------------------------------------
    def test_get_users_empty(self):
        """Empty list on startup → 200 with empty list."""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_users_after_creation(self):
        """After creating one user, the list contains exactly 1 item."""
        self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    # ----------------------------------------------------------------
    # GET /api/v1/users/<id>  —  retrieval by ID
    # ----------------------------------------------------------------
    def test_get_user_by_id_success(self):
        """Retrieve an existing user by ID → 200."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        response = self.client.get(f'/api/v1/users/{created["id"]}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], created["id"])

    def test_get_user_not_found(self):
        """Non-existent ID → 404."""
        response = self.client.get(
            '/api/v1/users/00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------
    # PUT /api/v1/users/<id>  —  update
    # ----------------------------------------------------------------
    def test_update_user_success(self):
        """Update first_name and last_name → 200 with new values."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        response = self.client.put(f'/api/v1/users/{created["id"]}', json={
            "first_name": "Jane",
            "last_name": "Smith"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["last_name"], "Smith")

    def test_update_user_email_success(self):
        """Update email → 200 with new email."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        response = self.client.put(f'/api/v1/users/{created["id"]}', json={
            "email": "new.email@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "new.email@example.com")

    def test_update_user_invalid_email(self):
        """Update with invalid email → 400."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        response = self.client.put(f'/api/v1/users/{created["id"]}', json={
            "email": "not-valid"
        })
        self.assertEqual(response.status_code, 400)

    def test_update_user_duplicate_email(self):
        """Update email to an already used email → 409."""
        self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        user2 = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com"
        }).get_json()
        response = self.client.put(f'/api/v1/users/{user2["id"]}', json={
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 409)

    def test_update_user_not_found(self):
        """Update a non-existent user → 404."""
        response = self.client.put(
            '/api/v1/users/00000000-0000-0000-0000-000000000000',
            json={"first_name": "Ghost"}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_id_is_forbidden(self):
        """Attempting to modify the id field → id remains unchanged."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        original_id = created["id"]
        self.client.put(f'/api/v1/users/{original_id}', json={
            "id": "00000000-0000-0000-0000-000000000000",
            "first_name": "Jane"
        })
        response = self.client.get(f'/api/v1/users/{original_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], original_id)

    def test_update_user_is_admin_is_forbidden(self):
        """Attempting to set is_admin to True → is_admin remains False."""
        created = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }).get_json()
        self.client.put(f'/api/v1/users/{created["id"]}', json={
            "is_admin": True,
            "first_name": "John"
        })
        with self.app.app_context():
            from app.services import facade
            user = facade.get_user(created["id"])
            self.assertFalse(user.is_admin)


if __name__ == '__main__':
    unittest.main()
