#!/usr/bin/python3
"""
Application entry point.

This module creates the Flask application instance using the
application factory and runs the development server.

It serves as the main execution point for starting the HBnB API
and runs the Flask development server.
"""


from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
