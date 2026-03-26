from .facade import HBnBFacade
"""
Service layer package initialization.

This module exposes a single shared instance of the HBnBFacade, which acts
as the main entry point for business logic operations throughout the
application.

The facade centralizes interactions between the API layer and the
persistence layer, making the application architecture cleaner and easier
to maintain.
"""

facade = HBnBFacade()
