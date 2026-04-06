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
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False


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
