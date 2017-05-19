from __future__ import unicode_literals
import os, sys, datetime

class Config(object):
    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    MONGODB_SETTINGS = {'DB': 'News'}
    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
    STATIC_PATH = os.path.join(BASE_DIR, 'static').replace('\\', '/')

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG = True

class PrdConfig(Config):
    # DEBUG = False
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    MONGODB_SETTINGS = {
        'db': os.environ.get('DB_NAME') or 'News',
        'host': os.environ.get('MONGO_HOST') or 'localhost',
    }

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGODB_SETTINGS = {
        'DB': 'NewsTest'
    }

config = {
    'dev': DevConfig,
    'prd': PrdConfig,
    'testing': TestingConfig,
    'default': DevConfig,
}
