#!/usr/bin/python3
"""
Services package initialization.

This module creates a single shared instance of the HBnBFacade
class that will be used across the application.

The facade serves as the central access point between the
Presentation layer (API) and the underlying business logic
and persistence layers.
"""


from app.services.facade import HBnBFacade

facade = HBnBFacade()
