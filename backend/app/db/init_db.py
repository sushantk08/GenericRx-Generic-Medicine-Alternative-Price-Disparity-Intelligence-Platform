from pathlib import Path
import sys

# Ensure project root is in sys.path when running script directly
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.db.session import Base, engine
# Import models so Base registers them
from backend.app.models.medicine import BrandedMedicine, GenericMedicine, Salt
from sqlalchemy import inspect


def init_db():
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables present in database: {tables}")

    required_tables = {"salts", "branded_medicines", "generic_medicines"}
    if required_tables.issubset(set(tables)):
        print(
            "All required tables (salts, branded_medicines, generic_medicines) successfully created!"
        )
    else:
        print(f"Warning: Missing tables: {required_tables - set(tables)}")


if __name__ == "__main__":
    init_db()