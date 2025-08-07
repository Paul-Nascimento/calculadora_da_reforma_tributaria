# config.py
import os

class Config:
    DEBUG = False
    TESTING = False
    API_PREFIX = "/"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")  # múltiplas origens

class DevConfig(Config):
    DEBUG = True
    CORS_ORIGINS = ["https://calculadora-da-reforma-frontend.vercel.app/"]

class ProdConfig(Config):
    pass

