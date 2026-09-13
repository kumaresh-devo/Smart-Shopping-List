import pymysql
from config import Config
from app import create_app
from models import db

def init_database():
    """Ensure MySQL database exists and create tables."""
    print("Connecting to MySQL to verify database existence...")
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=int(Config.MYSQL_PORT),
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{Config.MYSQL_DB}' confirmed.")
    conn.close()

    app = create_app()
    with app.app_context():
        print("Creating all tables via SQLAlchemy...")
        db.create_all()
        print("All tables successfully created in MySQL!")

if __name__ == '__main__':
    init_database()
