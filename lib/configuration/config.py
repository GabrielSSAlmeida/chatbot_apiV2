from datetime import timedelta
class Config:
    SQLALCHEMY_DATABASE_URI  = 'sqlite:///database.db'
    SECRET_KEY = 'secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False