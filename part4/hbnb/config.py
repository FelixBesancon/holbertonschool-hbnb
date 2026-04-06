#!/usr/bin/python3
"""
Application configuration module.

This module defines configuration classes used to manage
environment-specific settings for the HBnB application.

Different configurations (development, production, etc.)
can be defined by extending the base Config class.
"""


import os


class Config:
    """
    Base configuration class.

    Attributes:
        SECRET_KEY (str): Secret key used for session security.
        DEBUG (bool): Enables or disables debug mode.
        SQLALCHEMY_DATABASE_URI (str): Database connection string.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable SQLAlchemy event tracking.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hbnb.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """
    Development environment configuration.

    Inherits from Config and enables debug mode.
    """
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
