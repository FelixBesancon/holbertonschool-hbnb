#!/usr/bin/python3
"""
This module provides the create_app function
It defines the Flask application factory used to initialize the HBnB API
and configure Flask-RESTx.
"""


from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.reviews import api as reviews_ns


def create_app():
    """
    Application factory function.

    Creates and configures the Flask application instance,
    initializes the Flask-RESTx API, and prepares the
    structure for registering namespaces and endpoints.

    Returns:
        Flask: The configured Flask application instance.
        """
    app = Flask(__name__)
    api = Api(
        app, version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/'
        )

    # Register the users namespace
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    return app
