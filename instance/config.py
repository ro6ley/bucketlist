#!./bl-env/bin/python


class Config(object):
    """Parent configuration class"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flask_api.db'


class DevelopmentConfig(Config):
    """Config for development"""
    DEBUG = True


class TestingConfig(Config):
    """Config for testing purposes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_db.db'
    DEBUG = True


class StagingConfig(Config):
    """Config for staging"""
    DEBUG = True


class ProductionConfig(Config):
    """Config for Production"""
    DEBUG = False
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
