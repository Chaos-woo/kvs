import os
import sys
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

def is_development_mode():
    """
    Detect if we're running in development mode.
    In development: running from source code
    In production: running as bundled exe
    """
    # Check if we're running from a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return False

    # Check if we're in a typical development environment
    # (running from source with python interpreter)
    return True

def get_app_data_dir():
    """Get the appropriate application data directory for Windows"""
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA')
        if app_data:
            return os.path.join(app_data, 'kvs')

    # Fallback to current directory if not Windows or APPDATA not available
    return BASE_DIR

# Determine paths based on environment
if is_development_mode():
    # Development mode: keep current implementation
    DATA_DIR = BASE_DIR
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'kvs.db')
else:
    # Production mode: use Windows standard app data directory
    DATA_DIR = get_app_data_dir()
    os.makedirs(DATA_DIR, exist_ok=True)
    SQLITE_DB_PATH = os.path.join(DATA_DIR, 'kvs.db')

# Database configuration
SQLALCHEMY_DATABASE_URI = f'sqlite:///{SQLITE_DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application configuration
DEBUG = True
SECRET_KEY = 'dev-secret-key'  # Change this in production

# API configuration
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# Logging configuration
if is_development_mode():
    # Development mode: keep logs in backend directory
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
else:
    # Production mode: use Windows standard app data directory
    LOG_DIR = os.path.join(DATA_DIR, 'logs')

os.makedirs(LOG_DIR, exist_ok=True)
API_LOG_FILE = os.path.join(LOG_DIR, 'api.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')
FRONTEND_LOG_FILE = os.path.join(LOG_DIR, 'frontend.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
