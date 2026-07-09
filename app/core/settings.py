from app.core.config import *

def get_app_info():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "debug": DEBUG
    }