# -*- coding: utf-8 -*-
"""Application configuration."""
import os
import socket 

hostname = socket.gethostname()

class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('SOKO_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    UPLOAD_FOLDER = PROJECT_ROOT + "/soko/static/uploads/"
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SUPPRESS_SEND = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/soko_mkononi'  # TODO: Change me
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    # DB_NAME = 'dev.db'
    SECRET_KEY = os.environ.get('SOKO_SECRET', 'secret-key')  # TODO: Change me
    DB_NAME = 'soko_mkononi'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)

    if hostname == "paul-pro":
        SQLALCHEMY_DATABASE_URI = 'postgresql://paul@localhost/soko_mkononi'
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:jamonjuguna@localhost/soko_mkononi'  # TODO: Change me
        
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    MAIL_SERVER = 'smtp.tracom.co.ke'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'soko'
    MAIL_PASSWORD = 'Tr@c0m1234!'


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
