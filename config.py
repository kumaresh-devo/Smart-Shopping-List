import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-shopping-list-secret-key-change-me')
    
    # MySQL Database Connection Parameters (supports both MYSQL_* and DB_* prefixes)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or os.environ.get('DB_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or os.environ.get('DB_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or os.environ.get('DB_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') if 'MYSQL_PASSWORD' in os.environ else os.environ.get('DB_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB') or os.environ.get('DB_NAME') or 'smart_shopping_list'
    
    # Password encoding for URL (handles special characters like @, #, etc.)
    encoded_password = urllib.parse.quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ''
    auth_part = f"{MYSQL_USER}:{encoded_password}" if encoded_password else MYSQL_USER
    
    # SQLAlchemy Database URI - strictly MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"mysql+pymysql://{auth_part}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True
    }
