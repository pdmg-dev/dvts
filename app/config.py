import os


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    match env:
        case "production":
            return ProductionConfig()
        case "testing":
            return TestingConfig()
        case _:
            return DevelopmentConfig()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///test.db")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db")
