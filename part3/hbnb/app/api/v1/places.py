#!/usr/bin/python3
"""
Places API module.

This module defines the REST API endpoints for managing places in the HBnB
application, using Flask-RESTx.

Routes implemented:
- POST    Create a new place
- GET     List all places
- GET     Retrieve a place by ID (with owner, amenities, reviews)
- PUT     Update a place (no owner_id update)
- GET     List all reviews for a place

The persistence and business rules are handled
by the facade (HBnBFacade).
"""


from flask_restx import Namespace, Resource, fields
from app.services import facade


api = Namespace('places', description='Place operations')

# ------------------------------------------------------------
# ---------------------- API MODELS --------------------------
# ------------------------------------------------------------
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Documentation / "full" place shape (mostly used for output docs)
place_model = api.model('Place', {
    'title': fields.String(
        required=True, description='Title of the place'
        ),
    'description': fields.String(
        description='Description of the place'
        ),
    'price': fields.Float(
        required=True, description='Price per night'
        ),
    'latitude': fields.Float(
        required=True, description='Latitude of the place'
        ),
    'longitude': fields.Float(
        required=True, description='Longitude of the place'
        ),
    'owner_id': fields.String(
        required=True, description='ID of the owner'
        ),
    'owner': fields.Nested(
        user_model, description='Owner of the place'
        ),
    'amenities': fields.List(
        fields.Nested(amenity_model), description='List of amenities'
        ),
    'reviews': fields.List(
        fields.Nested(review_model), description='List of reviews'
        )
})

# Input model for create
place_create_model = api.model('PlaceCreate', {
    'title': fields.String(
        required=True, description='Title of the place'
        ),
    'description': fields.String(
        required=False, description='Description of the place'
        ),
    'price': fields.Float(
        required=True, description='Price per night'
        ),
    'latitude': fields.Float(
        required=True, description='Latitude of the place'
        ),
    'longitude': fields.Float(
        required=True, description='Longitude of the place'
        ),
    'owner_id': fields.String(
        required=True, description='ID of the owner'
        ),
    'amenities': fields.List(
        fields.String,
        required=True,
        description="List of amenity IDs"
        )
})

# Input model for update (fields optional)
place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(
        required=False, description='Title of the place'
        ),
    'description': fields.String(
        required=False, description='Description of the place'
        ),
    'price': fields.Float(
        required=False, description='Price per night'
        ),
    'latitude': fields.Float(
        required=False, description='Latitude of the place'
        ),
    'longitude': fields.Float(
        required=False, description='Longitude of the place'
        ),
    'amenities': fields.List(
        fields.String, required=False, description="List of amenity IDs"
        )
})


# ------------------------------------------------------------
# ------------------------ RESOURCES -------------------------
# ------------------------------------------------------------
@api.route('/')
class PlaceList(Resource):
    """
    Resource for creating and listing places.
    """

    @api.expect(place_create_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """
        Register a new place.

        Validations:
        - Owner must exist (checked via facade)
        - Model validations (title/price/lat/long/UUIDs)
          are enforced by Place()

        Returns:
            tuple: (response_body, status_code)
        """
        payload = api.payload

        # Ensure owner exists (consistent with create_review checks)
        owner = facade.get_user(payload['owner_id'])
        if not owner:
            return {'error': 'Owner not found'}, 400

        amenities = payload.get('amenities', [])
        if amenities is None:
            amenities = []
        if not isinstance(amenities, list):
            return {'error': 'amenities must be a list of amenity IDs'}, 400

        place_data = {
            'owner_id': payload['owner_id'],
            'title': payload['title'],
            'description': payload.get('description', ''),
            'price': payload['price'],
            'latitude': payload['latitude'],
            'longitude': payload['longitude'],
            'amenities': amenities
        }

        try:
            new_place = facade.create_place(place_data)
        except (TypeError, ValueError) as e:
            return {'error': str(e)}, 400

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'owner_id': new_place.owner_id
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """
        Retrieve a list of all places.

        Note:
            This endpoint returns a light representation of each place
            (id, title, latitude, longitude), as shown in the project examples.

        Returns:
            tuple: (list_of_places, status_code)
        """
        places = facade.get_all_places()
        return [
            {
                'id': p.id,
                'title': p.title,
                'latitude': p.latitude,
                'longitude': p.longitude
            }
            for p in places
        ], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    """
    Resource for retrieving and updating a specific place.
    """

    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve a place by its identifier.

        Includes:
        - owner details (nested)
        - amenities (currently returned as IDs only if
          amenity resolution is not available)
        - reviews for this place (nested)

        Returns:
            tuple: (place_details, status_code)
        """
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        owner = facade.get_user(place.owner_id)
        reviews = facade.get_reviews_by_place(place.id)

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'email': owner.email
            } if owner else None,
            'amenities': [
                {'id': amenity.id, 'name': amenity.name}
                for aid in place.amenity_ids
                for amenity in [facade.get_amenity(aid)]
                if amenity is not None
            ],
            'reviews': [
                {
                    'id': r.id,
                    'text': r.text,
                    'rating': r.rating,
                    'user_id': r.user_id
                }
                for r in reviews
            ]
        }, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """
        Update a place's information.

        Notes:
        - owner_id is protected in the facade and cannot be updated.
        - amenities are handled explicitly here (stored in amenity_ids).

        Returns:
            tuple: (updated_place, status_code)
        """
        payload = api.payload

        if 'amenities' in payload and payload['amenities'] is not None:
            if not isinstance(payload['amenities'], list):
                return {
                    'error': 'amenities must be a list of amenity IDs'
                    }, 400

        try:
            updated = facade.update_place(place_id, payload)
        except (TypeError, ValueError) as e:
            return {'error': str(e)}, 400

        if not updated:
            return {'error': 'Place not found'}, 404

        return {'message': 'Place updated successfully'}, 200


@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    """
    Resource for listing reviews belonging to a given place.
    """

    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve all reviews associated with a specific place.

        Returns:
            tuple: (list_of_reviews, status_code)
        """
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        reviews = facade.get_reviews_by_place(place_id)
        return [
            {
                'id': r.id,
                'text': r.text,
                'rating': r.rating,
                'user_id': r.user_id,
                'place_id': r.place_id
            }
            for r in reviews
        ], 200
