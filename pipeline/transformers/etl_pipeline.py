import json
from pathlib import Path
import numpy as np
import pandas as pd

from pipeline.transformers.price_calculator import (
    calculate_price_per_unit,
    parse_pack_size,
)
from pipeline.transformers.salt_normalizer import (
    clean_salt_name,
    parse_dosage,
)

# Core chronic medicines baseline (Diabetes, Hypertension, Cholesterol, Gastric)
SEED_BRANDED_DATA = [
    {
        "brand_name": "Telma 40 Tablet",
        "manufacturer": "Glenmark Pharmaceuticals",
        "raw_composition": "Telmisartan (40mg)",
        "pack_size": "10 Tablets in 1 Strip",
        "mrp": "140.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Glycomet 500 SR Tablet",
        "manufacturer": "USV Ltd",
        "raw_composition": "Metformin Hydrochloride (500mg)",
        "pack_size": "10's",
        "mrp": "46.50",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Atorva 10 Tablet",
        "manufacturer": "Zydus Cadila",
        "raw_composition": "Atorvastatin (10mg)",
        "pack_size": "15 Tablets",
        "mrp": "115.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Amlong 5 Tablet",
        "manufacturer": "Micro Labs Ltd",
        "raw_composition": "Amlodipine Besylate (5mg)",
        "pack_size": "15's",
        "mrp": "78.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Pan 40 Tablet",
        "manufacturer": "Alkem Laboratories",
        "raw_composition": "Pantoprazole Sodium (40mg)",
        "pack_size": "15 Tablets",
        "mrp": "155.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Rosuvas 10 Tablet",
        "manufacturer": "Sun Pharmaceutical",
        "raw_composition": "Rosuvastatin (10mg)",
        "pack_size": "10 Tablets",
        "mrp": "185.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
    {
        "brand_name": "Dolo 650 Tablet",
        "manufacturer": "Micro Labs Ltd",
        "raw_composition": "Paracetamol (650mg)",
        "pack_size": "15's",
        "mrp": "34.00",
        "dosage_form": "Tablet",
        "source": "Retail Catalog",
    },
]

SEED_GENERIC_DATA = [
    {
        "name": "Telmisartan Tablets IP 40mg",
        "raw_composition": "Telmisartan 40mg",
        "pack_size": "10 Tablets",
        "mrp": "18.00",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Metformin Hydrochloride PR Tablets IP 500mg",
        "raw_composition": "Metformin HCL 500mg",
        "pack_size": "10 Tablets",
        "mrp": "7.20",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Atorvastatin Tablets IP 10mg",
        "raw_composition": "Atorvastatin Calcium 10mg",
        "pack_size": "10 Tablets",
        "mrp": "14.50",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Amlodipine Tablets IP 5mg",
        "raw_composition": "Amlodipine 5mg",
        "pack_size": "10 Tablets",
        "mrp": "6.00",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Pantoprazole Gastro-Resistant Tablets IP 40mg",
        "raw_composition": "Pantoprazole 40mg",
        "pack_size": "10 Tablets",
        "mrp": "15.00",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Rosuvastatin Tablets IP 10mg",
        "raw_composition": "Rosuvastatin 10mg",
        "pack_size": "10 Tablets",
        "mrp": "24.00",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
    {
        "name": "Paracetamol Tablets IP 650mg",
        "raw_composition": "Paracetamol 650mg",
        "pack_size": "10 Tablets",
        "mrp": "10.50",
        "dosage_form": "Tablet",
        "source": "Jan Aushadhi (PMBJP)",
    },
]


def load_raw_dataset(file_path: Path, fallback_data: list) -> pd.DataFrame:
    """Load JSON scraped data if exists, otherwise fallback to seed data."""
    if file_path.exists() and file_path.stat().st_size > 10:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    print(
                        f"Loaded {len(data)} records from {file_path.name}"
                    )
                    return pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}. Using seed records.")
    print(f"Using {len(fallback_data)} seed records for {file_path.stem}")
    return pd.DataFrame(fallback_data)


def run_etl():
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("Starting GenericRx ETL Pipeline...")

    # 1. Load Raw Datasets
    df_branded = load_raw_dataset(
        raw_dir / "branded_medicines_raw.json", SEED_BRANDED_DATA
    )
    df_generic = load_raw_dataset(
        raw_dir / "janaushadhi_raw.json", SEED_GENERIC_DATA
    )

    # 2. Clean and Normalize Branded Medicines
    print("Normalizing branded medicines...")
    df_branded["std_salt_name"] = df_branded["raw_composition"].apply(
        clean_salt_name
    )

    dosage_info = df_branded["raw_composition"].apply(parse_dosage)
    df_branded["strength_value"] = [d[0] for d in dosage_info]
    df_branded["strength_unit"] = [d[1] for d in dosage_info]
    df_branded["dosage_form"] = [d[2] for d in dosage_info]

    df_branded["clean_pack_size"] = df_branded["pack_size"].apply(
        parse_pack_size
    )
    df_branded["price_per_unit"] = [
        calculate_price_per_unit(mrp, pack)
        for mrp, pack in zip(df_branded["mrp"], df_branded["clean_pack_size"])
    ]
    df_branded["clean_mrp"] = df_branded["mrp"].apply(
        lambda x: float(str(x).replace("₹", "").replace("Rs.", "").strip())
    )

    # 3. Clean and Normalize Generic Medicines
    print("Normalizing generic medicines...")
    df_generic["std_salt_name"] = df_generic["raw_composition"].apply(
        clean_salt_name
    )

    generic_dosage = df_generic["raw_composition"].apply(parse_dosage)
    df_generic["strength_value"] = [d[0] for d in generic_dosage]
    df_generic["strength_unit"] = [d[1] for d in generic_dosage]
    df_generic["dosage_form"] = [d[2] for d in generic_dosage]

    df_generic["clean_pack_size"] = df_generic["pack_size"].apply(
        parse_pack_size
    )
    df_generic["price_per_unit"] = [
        calculate_price_per_unit(mrp, pack)
        for mrp, pack in zip(df_generic["mrp"], df_generic["clean_pack_size"])
    ]
    df_generic["clean_mrp"] = df_generic["mrp"].apply(
        lambda x: float(str(x).replace("₹", "").replace("Rs.", "").strip())
    )

    # 4. Create Master Salts DataFrame (Unique combinations)
    print("Extracting unique salt masters...")
    salts_combined = pd.concat(
        [
            df_branded[
                [
                    "std_salt_name",
                    "strength_value",
                    "strength_unit",
                    "dosage_form",
                ]
            ],
            df_generic[
                [
                    "std_salt_name",
                    "strength_value",
                    "strength_unit",
                    "dosage_form",
                ]
            ],
        ]
    ).drop_duplicates()

    salts_combined = salts_combined[salts_combined["std_salt_name"] != ""]
    salts_combined.reset_index(drop=True, inplace=True)
    salts_combined["salt_id"] = salts_combined.index + 1
    salts_combined.rename(columns={"std_salt_name": "salt_name"}, inplace=True)

    # 5. Map salt_id back to Branded and Generic tables
    df_branded = df_branded.merge(
        salts_combined,
        left_on=[
            "std_salt_name",
            "strength_value",
            "strength_unit",
            "dosage_form",
        ],
        right_on=[
            "salt_name",
            "strength_value",
            "strength_unit",
            "dosage_form",
        ],
        how="inner",
    )

    df_generic = df_generic.merge(
        salts_combined,
        left_on=[
            "std_salt_name",
            "strength_value",
            "strength_unit",
            "dosage_form",
        ],
        right_on=[
            "salt_name",
            "strength_value",
            "strength_unit",
            "dosage_form",
        ],
        how="inner",
    )

    # 6. Prepare Final Columns Matching PostgreSQL Schema
    salts_export = salts_combined[
        ["salt_id", "salt_name", "strength_value", "strength_unit", "dosage_form"]
    ]

    branded_export = df_branded[
        [
            "brand_name",
            "salt_id",
            "manufacturer",
            "clean_pack_size",
            "clean_mrp",
            "price_per_unit",
        ]
    ].rename(columns={"clean_pack_size": "pack_size", "clean_mrp": "mrp"})

    generic_export = df_generic[
        [
            "name",
            "salt_id",
            "source",
            "clean_pack_size",
            "clean_mrp",
            "price_per_unit",
        ]
    ].rename(
        columns={
            "name": "generic_name",
            "clean_pack_size": "pack_size",
            "clean_mrp": "mrp",
        }
    )

    # 7. Save Processed Datasets
    salts_export.to_csv(processed_dir / "salts_clean.csv", index=False)
    branded_export.to_csv(
        processed_dir / "branded_medicines_clean.csv", index=False
    )
    generic_export.to_csv(
        processed_dir / "generic_medicines_clean.csv", index=False
    )

    print(f"ETL Finished successfully:")
    print(f" -> {len(salts_export)} active salts saved to salts_clean.csv")
    print(
        f" -> {len(branded_export)} branded drugs saved to branded_medicines_clean.csv"
    )
    print(
        f" -> {len(generic_export)} generic alternatives saved to generic_medicines_clean.csv"
    )


if __name__ == "__main__":
    run_etl()