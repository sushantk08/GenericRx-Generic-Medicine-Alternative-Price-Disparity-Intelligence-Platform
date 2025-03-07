from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import text

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.db.session import SessionLocal, engine
from backend.app.models.medicine import BrandedMedicine, GenericMedicine, Salt


def seed_database():
    processed_dir = project_root / "data" / "processed"
    salts_csv = processed_dir / "salts_clean.csv"
    branded_csv = processed_dir / "branded_medicines_clean.csv"
    generic_csv = processed_dir / "generic_medicines_clean.csv"

    if (
        not salts_csv.exists()
        or not branded_csv.exists()
        or not generic_csv.exists()
    ):
        print(
            "Error: Processed CSV files not found. Run pipeline/transformers/etl_pipeline.py first."
        )
        return

    print("Loading cleaned datasets from data/processed/...")
    df_salts = pd.read_csv(salts_csv)
    df_branded = pd.read_csv(branded_csv)
    df_generic = pd.read_csv(generic_csv)

    db = SessionLocal()
    try:
        # Clear existing entries in reverse foreign key order for clean idempotency
        print("Resetting existing tables...")
        db.query(BrandedMedicine).delete()
        db.query(GenericMedicine).delete()
        db.query(Salt).delete()
        db.commit()

        # Reset serial sequences in PostgreSQL
        with engine.connect() as conn:
            conn.execute(
                text("ALTER SEQUENCE salts_id_seq RESTART WITH 1;")
            )
            conn.execute(
                text("ALTER SEQUENCE branded_medicines_id_seq RESTART WITH 1;")
            )
            conn.execute(
                text("ALTER SEQUENCE generic_medicines_id_seq RESTART WITH 1;")
            )
            conn.commit()

        # 1. Insert Salts and build ID map
        print("Inserting salts...")
        salt_id_map = {}  # maps original CSV salt_id to new database Salt.id
        for _, row in df_salts.iterrows():
            salt_obj = Salt(
                salt_name=str(row["salt_name"]).strip(),
                strength_value=float(row["strength_value"]),
                strength_unit=str(row["strength_unit"]).strip(),
                dosage_form=str(row["dosage_form"]).strip(),
            )
            db.add(salt_obj)
            db.flush()  # flushes to assign primary key salt_obj.id
            salt_id_map[row["salt_id"]] = salt_obj.id

        db.commit()
        print(f" -> Inserted {len(salt_id_map)} salts.")

        # 2. Insert Branded Medicines
        print("Inserting branded medicines...")
        branded_objs = []
        for _, row in df_branded.iterrows():
            db_salt_id = salt_id_map.get(row["salt_id"])
            if db_salt_id:
                branded_objs.append(
                    BrandedMedicine(
                        brand_name=str(row["brand_name"]).strip(),
                        salt_id=db_salt_id,
                        manufacturer=str(row.get("manufacturer", "Unknown")),
                        pack_size=int(row["pack_size"]),
                        mrp=float(row["mrp"]),
                        price_per_unit=float(row["price_per_unit"]),
                    )
                )
        db.bulk_save_objects(branded_objs)
        db.commit()
        print(f" -> Inserted {len(branded_objs)} branded medicines.")

        # 3. Insert Generic Medicines
        print("Inserting generic medicines...")
        generic_objs = []
        for _, row in df_generic.iterrows():
            db_salt_id = salt_id_map.get(row["salt_id"])
            if db_salt_id:
                generic_objs.append(
                    GenericMedicine(
                        generic_name=str(row["generic_name"]).strip(),
                        salt_id=db_salt_id,
                        source=str(row.get("source", "Jan Aushadhi (PMBJP)")),
                        pack_size=int(row["pack_size"]),
                        mrp=float(row["mrp"]),
                        price_per_unit=float(row["price_per_unit"]),
                    )
                )
        db.bulk_save_objects(generic_objs)
        db.commit()
        print(f" -> Inserted {len(generic_objs)} generic medicines.")

        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()