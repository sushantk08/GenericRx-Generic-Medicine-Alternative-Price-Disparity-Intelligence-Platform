import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()


PG_USER = os.getenv("POSTGRES_USER", "genericrx")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "genericrx_db")


MONGO_USER = os.getenv("MONGO_USER", "genericrx")
MONGO_PASS = os.getenv("MONGO_PASSWORD", "")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27018")

POSTGRES_URL = f"postgresql+psycopg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"


def test_postgres():
    print("Testing PostgreSQL connection...")
    try:
        engine = create_engine(POSTGRES_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print(f"PostgreSQL connection successful: {result[0][:45]}...")
            return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False


def test_mongodb():
    print("Testing MongoDB connection...")
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("MongoDB connection successful: ping response received.")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False


def main():
    pg_ok = test_postgres()
    mongo_ok = test_mongodb()

    if pg_ok and mongo_ok:
        print("\nAll database services are connected and healthy.")
        sys.exit(0)
    else:
        print("\nOne or more database connection tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()