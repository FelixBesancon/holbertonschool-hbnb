import os


class Config:
    """
    Base configuration class for the HBnB application.

    This class defines the default configuration values shared across
    all application environments. It is intended to be extended by more
    specific configuration classes, such as development or production
    configurations.

    Attributes:
        SECRET_KEY (str): Secret key used by Flask to secure sessions,
            tokens, and other sensitive application features.
        DEBUG (bool): Flag indicating whether debug mode is enabled.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Development configuration class for the HBnB application.

    This configuration enables debug mode and uses a local SQLite
    database for development purposes.

    Attributes:
        DEBUG (bool): Enables Flask debug mode.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI for the
            local SQLite development database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disables SQLAlchemy's
            modification tracking system to reduce overhead.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
