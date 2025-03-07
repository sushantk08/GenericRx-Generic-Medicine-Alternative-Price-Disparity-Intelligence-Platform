from pathlib import Path
import sys
from sqlalchemy import text

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.db.session import engine


def apply_indexes():
    print("Enabling pg_trgm extension and creating GIN indexes...")
    with engine.connect() as conn:
        # Enable extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        # Create GIN trigram indexes
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_branded_name_trgm ON branded_medicines USING gin (brand_name gin_trgm_ops);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_generic_name_trgm ON generic_medicines USING gin (generic_name gin_trgm_ops);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_salts_name_trgm ON salts USING gin (salt_name gin_trgm_ops);"
            )
        )
        conn.commit()

        # Verify created indexes in pg_indexes
        result = conn.execute(
            text(
                "SELECT indexname FROM pg_indexes WHERE indexname LIKE '%_trgm';"
            )
        ).fetchall()

        created_indexes = [r[0] for r in result]
        print(
            f"Verified active trigram indexes in PostgreSQL: {created_indexes}"
        )
        print("Trigram indexing applied successfully!")


if __name__ == "__main__":
    apply_indexes()