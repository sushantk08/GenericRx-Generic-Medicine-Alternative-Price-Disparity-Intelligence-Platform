import json
from pathlib import Path
import random

# Seed for deterministic generation
random.seed(42)

# Therapeutic Categories with core active salts, common strengths, forms, and base branded prices
THERAPEUTIC_SALTS = [
    # Cardiovascular & Hypertension
    {
        "salt": "Telmisartan",
        "strengths": [20, 40, 80],
        "unit": "mg",
        "form": "Tablet",
        "category": "Cardiovascular",
        "brands": [
            ("Telma", "Glenmark Pharmaceuticals"),
            ("Telpres", "Abbott Healthcare"),
            ("Telsartan", "Dr. Reddy's Laboratories"),
            ("Telmikind", "Mankind Pharma"),
            ("Arbitel", "Micro Labs"),
            ("Telista", "Cadila Pharmaceuticals"),
        ],
        "base_price_per_unit": 12.50,
    },
    {
        "salt": "Amlodipine",
        "strengths": [2.5, 5, 10],
        "unit": "mg",
        "form": "Tablet",
        "category": "Cardiovascular",
        "brands": [
            ("Amlong", "Micro Labs"),
            ("Amlopin", "USV Ltd"),
            ("Stamlo", "Dr. Reddy's Laboratories"),
            ("Amlovas", "Macleods Pharmaceuticals"),
            ("Amlokind", "Mankind Pharma"),
        ],
        "base_price_per_unit": 6.80,
    },
    {
        "salt": "Atorvastatin",
        "strengths": [10, 20, 40, 80],
        "unit": "mg",
        "form": "Tablet",
        "category": "Cardiovascular",
        "brands": [
            ("Atorva", "Zydus Cadila"),
            ("Storvas", "Sun Pharmaceutical"),
            ("Lipikind", "Mankind Pharma"),
            ("Atocor", "Dr. Reddy's Laboratories"),
            ("Tonact", "Lupin Ltd"),
            ("Aztor", "Torrent Pharmaceuticals"),
        ],
        "base_price_per_unit": 14.20,
    },
    {
        "salt": "Rosuvastatin",
        "strengths": [5, 10, 20, 40],
        "unit": "mg",
        "form": "Tablet",
        "category": "Cardiovascular",
        "brands": [
            ("Rosuvas", "Sun Pharmaceutical"),
            ("Rozucor", "Torrent Pharmaceuticals"),
            ("Roseday", "USV Ltd"),
            ("Rosulip", "Cipla Ltd"),
            ("Rosave", "Alembic Pharmaceuticals"),
        ],
        "base_price_per_unit": 18.50,
    },
    # Diabetes & Endocrinology
    {
        "salt": "Metformin Hydrochloride",
        "strengths": [250, 500, 850, 1000],
        "unit": "mg",
        "form": "Tablet",
        "category": "Anti-diabetic",
        "brands": [
            ("Glycomet", "USV Ltd"),
            ("Cetapin", "Sanofi India"),
            ("Glucophage", "Merck"),
            ("Metgem", "Metrix Healthcare"),
            ("Obimet", "Abbott India"),
            ("Bigomet", "Torrent Pharmaceuticals"),
        ],
        "base_price_per_unit": 4.50,
    },
    {
        "salt": "Glimepiride",
        "strengths": [1, 2, 3, 4],
        "unit": "mg",
        "form": "Tablet",
        "category": "Anti-diabetic",
        "brands": [
            ("Amaryl", "Sanofi India"),
            ("Glimestar", "Mankind Pharma"),
            ("Zoryl", "Intas Pharmaceuticals"),
            ("Gemer", "Sun Pharmaceutical"),
            ("Glimy", "Dr. Reddy's Laboratories"),
        ],
        "base_price_per_unit": 8.20,
    },
    {
        "salt": "Vildagliptin",
        "strengths": [50, 100],
        "unit": "mg",
        "form": "Tablet",
        "category": "Anti-diabetic",
        "brands": [
            ("Galvus", "Novartis India"),
            ("Jalra", "USV Ltd"),
            ("Zomelis", "Abbott Healthcare"),
            ("Vysov", "Torrent Pharmaceuticals"),
        ],
        "base_price_per_unit": 22.00,
    },
    {
        "salt": "Dapagliflozin",
        "strengths": [5, 10],
        "unit": "mg",
        "form": "Tablet",
        "category": "Anti-diabetic",
        "brands": [
            ("Forxiga", "AstraZeneca"),
            ("Oxra", "Sun Pharmaceutical"),
            ("Daflo", "Torrent Pharmaceuticals"),
            ("Dapaglyn", "Zydus Healthcare"),
        ],
        "base_price_per_unit": 38.00,
    },
    # Gastrointestinal
    {
        "salt": "Pantoprazole",
        "strengths": [20, 40],
        "unit": "mg",
        "form": "Tablet",
        "category": "Gastrointestinal",
        "brands": [
            ("Pan", "Alkem Laboratories"),
            ("Pantocid", "Sun Pharmaceutical"),
            ("Pantodac", "Zydus Cadila"),
            ("Pantocar", "Micro Labs"),
            ("Nupenta", "Macleods Pharmaceuticals"),
        ],
        "base_price_per_unit": 11.50,
    },
    {
        "salt": "Omeprazole",
        "strengths": [10, 20, 40],
        "unit": "mg",
        "form": "Capsule",
        "category": "Gastrointestinal",
        "brands": [
            ("Omez", "Dr. Reddy's Laboratories"),
            ("Omee", "Alkem Laboratories"),
            ("Omecip", "Cipla Ltd"),
            ("Ocid", "Zydus Cadila"),
        ],
        "base_price_per_unit": 7.40,
    },
    {
        "salt": "Rabeprazole",
        "strengths": [10, 20],
        "unit": "mg",
        "form": "Tablet",
        "category": "Gastrointestinal",
        "brands": [
            ("Rablet", "Lupin Ltd"),
            ("Happi", "Zydus Cadila"),
            ("Cyra", "Systopic Laboratories"),
            ("Razo", "Dr. Reddy's Laboratories"),
        ],
        "base_price_per_unit": 13.00,
    },
    # Antibiotics & Anti-infectives
    {
        "salt": "Amoxicillin",
        "strengths": [250, 500],
        "unit": "mg",
        "form": "Capsule",
        "category": "Antibiotic",
        "brands": [
            ("Mox", "Sun Pharmaceutical"),
            ("Novamox", "Cipla Ltd"),
            ("Almox", "Alkem Laboratories"),
            ("Amoxyclav", "Abbott India"),
        ],
        "base_price_per_unit": 10.50,
    },
    {
        "salt": "Azithromycin",
        "strengths": [250, 500],
        "unit": "mg",
        "form": "Tablet",
        "category": "Antibiotic",
        "brands": [
            ("Azithral", "Alembic Pharmaceuticals"),
            ("Azee", "Cipla Ltd"),
            ("Zithrox", "Macleods Pharmaceuticals"),
            ("Azimax", "Sun Pharmaceutical"),
        ],
        "base_price_per_unit": 24.00,
    },
    {
        "salt": "Ciprofloxacin",
        "strengths": [250, 500],
        "unit": "mg",
        "form": "Tablet",
        "category": "Antibiotic",
        "brands": [
            ("Cifran", "Sun Pharmaceutical"),
            ("Ciplox", "Cipla Ltd"),
            ("Ciprobid", "Zydus Cadila"),
            ("Zoxan", "FDC Ltd"),
        ],
        "base_price_per_unit": 9.50,
    },
    # Analgesics & Anti-inflammatory
    {
        "salt": "Paracetamol",
        "strengths": [500, 650],
        "unit": "mg",
        "form": "Tablet",
        "category": "Analgesic",
        "brands": [
            ("Dolo", "Micro Labs"),
            ("Calpol", "GlaxoSmithKline"),
            ("Pacimol", "Ipca Laboratories"),
            ("P-650", "Apex Laboratories"),
            ("Crocin", "GlaxoSmithKline"),
        ],
        "base_price_per_unit": 2.40,
    },
    {
        "salt": "Aceclofenac",
        "strengths": [100, 200],
        "unit": "mg",
        "form": "Tablet",
        "category": "Analgesic",
        "brands": [
            ("Hifenac", "Intas Pharmaceuticals"),
            ("Zerodol", "Ipca Laboratories"),
            ("Aceclo", "Aristo Pharmaceuticals"),
            ("Dolokind", "Mankind Pharma"),
        ],
        "base_price_per_unit": 8.50,
    },
    # Respiratory & Anti-allergy
    {
        "salt": "Montelukast",
        "strengths": [4, 5, 10],
        "unit": "mg",
        "form": "Tablet",
        "category": "Respiratory",
        "brands": [
            ("Montair", "Cipla Ltd"),
            ("Montek", "Sun Pharmaceutical"),
            ("Romilast", "Ranbaxy / Sun"),
            ("Telekast", "Lupin Ltd"),
        ],
        "base_price_per_unit": 16.00,
    },
    {
        "salt": "Levocetirizine",
        "strengths": [2.5, 5, 10],
        "unit": "mg",
        "form": "Tablet",
        "category": "Anti-allergy",
        "brands": [
            ("Levocet", "Hetero Healthcare"),
            ("Vozet", "Dr. Reddy's Laboratories"),
            ("1-AL", "FDC Ltd"),
            ("Lecope", "Mankind Pharma"),
            ("Levorid", "Cipla Ltd"),
        ],
        "base_price_per_unit": 6.20,
    },
    # Central Nervous System
    {
        "salt": "Clonazepam",
        "strengths": [0.25, 0.5, 1, 2],
        "unit": "mg",
        "form": "Tablet",
        "category": "Neurology",
        "brands": [
            ("Clona", "Consern Pharma"),
            ("Rivotril", "Abbott Healthcare"),
            ("Zapiz", "Intas Pharmaceuticals"),
            ("Epitril", "Novartis India"),
            ("Lonazep", "Sun Pharmaceutical"),
        ],
        "base_price_per_unit": 7.50,
    },
    {
        "salt": "Escitalopram",
        "strengths": [5, 10, 20],
        "unit": "mg",
        "form": "Tablet",
        "category": "Psychiatry",
        "brands": [
            ("Nexito", "Sun Pharmaceutical"),
            ("Cipralex", "Lundbeck India"),
            ("Stalopam", "Lupin Ltd"),
            ("S-Citadep", "Cipla Ltd"),
            ("Rexipra", "Intas Pharmaceuticals"),
        ],
        "base_price_per_unit": 12.00,
    },
    # Vitamins & Supplements
    {
        "salt": "Calcium Carbonate",
        "strengths": [250, 500],
        "unit": "mg",
        "form": "Tablet",
        "category": "Supplements",
        "brands": [
            ("Shelcal", "Torrent Pharmaceuticals"),
            ("Cipcal", "Cipla Ltd"),
            ("Gemcal", "Alkem Laboratories"),
            ("Calcimax", "Meyer Organics"),
        ],
        "base_price_per_unit": 8.00,
    },
    {
        "salt": "Cholecalciferol",
        "strengths": [1000, 2000, 60000],
        "unit": "iu",
        "form": "Capsule",
        "category": "Supplements",
        "brands": [
            ("Calcirol", "Cadila Pharmaceuticals"),
            ("D3 Must", "Mankind Pharma"),
            ("Uprise D3", "Alkem Laboratories"),
            ("Tayocal D3", "Torrent Pharmaceuticals"),
        ],
        "base_price_per_unit": 28.00,
    },
]

PACK_SIZE_OPTIONS = [
    ("10 Tablets in 1 Strip", 10),
    ("Strip of 15 Tablets", 15),
    ("10's", 10),
    ("Strip of 10", 10),
    ("Bottle of 30 Capsules", 30),
]

SUFFIXES = [
    "",
    "SR",
    "PR",
    "ER",
    "CR",
    "Forte",
    "Plus",
    "OD",
    "Duo",
    "Tablet IP",
]


def generate_datasets(target_branded_count=3000):
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"Generating {target_branded_count} medicine records across 22 major active chemical salts..."
    )

    branded_medicines = []
    generic_medicines = []
    generic_seen = set()

    code_counter = 1000

    # 1. Generate Jan Aushadhi Generic catalog for every salt & strength combination
    for item in THERAPEUTIC_SALTS:
        salt_name = item["salt"]
        unit = item["unit"]
        form = item["form"]

        for strength in item["strengths"]:
            key = (salt_name, strength, unit, form)
            if key not in generic_seen:
                generic_seen.add(key)
                code_counter += 1

                # Jan Aushadhi pricing: 65% to 85% discount relative to market
                market_base = item["base_price_per_unit"] * (
                    1 + (strength / max(item["strengths"])) * 0.5
                )
                discount_pct = random.uniform(0.65, 0.85)
                generic_unit_price = round(market_base * (1 - discount_pct), 2)
                generic_unit_price = max(generic_unit_price, 0.50)  # min 50p

                pack_count = 10
                generic_mrp = round(generic_unit_price * pack_count, 2)

                generic_medicines.append(
                    {
                        "drug_code": f"G{code_counter}",
                        "name": f"{salt_name} {form}s IP {strength}{unit}",
                        "raw_composition": f"{salt_name} {strength}{unit}",
                        "pack_size": f"{pack_count} {form}s",
                        "mrp": str(generic_mrp),
                        "dosage_form": form,
                        "category": item["category"],
                        "source": "Jan Aushadhi (PMBJP)",
                    }
                )

    # 2. Generate 3,000 Branded Medicines by combining brands, strengths, pack sizes & suffixes
    counter = 0
    while len(branded_medicines) < target_branded_count:
        for item in THERAPEUTIC_SALTS:
            if len(branded_medicines) >= target_branded_count:
                break

            salt_name = item["salt"]
            unit = item["unit"]
            form = item["form"]

            for brand_base, manufacturer in item["brands"]:
                if len(branded_medicines) >= target_branded_count:
                    break

                for strength in item["strengths"]:
                    if len(branded_medicines) >= target_branded_count:
                        break

                    pack_str, pack_count = random.choice(PACK_SIZE_OPTIONS)
                    suffix = random.choice(SUFFIXES)

                    name_parts = [brand_base, str(strength)]
                    if suffix:
                        name_parts.append(suffix)
                    if form not in name_parts:
                        name_parts.append(form)
                    brand_name = " ".join(name_parts)

                    # Realistic market branded pricing
                    base_unit_rate = item["base_price_per_unit"] * (
                        1 + (strength / max(item["strengths"])) * 0.5
                    )
                    random_premium = random.uniform(0.9, 1.3)
                    unit_price = round(base_unit_rate * random_premium, 2)
                    mrp = round(unit_price * pack_count, 2)

                    composition_formats = [
                        f"{salt_name} ({strength}{unit})",
                        f"Tab. {salt_name} {strength} {unit}",
                        f"{salt_name} IP {strength}{unit}",
                        f"{salt_name} Hydrochloride {strength}{unit}"
                        if "Hydrochloride" not in salt_name
                        else f"{salt_name} {strength}{unit}",
                    ]
                    raw_comp = random.choice(composition_formats)

                    branded_medicines.append(
                        {
                            "brand_name": brand_name,
                            "manufacturer": manufacturer,
                            "raw_composition": raw_comp,
                            "pack_size": pack_str,
                            "mrp": str(mrp),
                            "dosage_form": form,
                            "category": item["category"],
                            "source": "Indian Retail Pharmacy Catalog",
                        }
                    )

    # Save to data/raw/
    branded_file = raw_dir / "branded_medicines_raw.json"
    generic_file = raw_dir / "janaushadhi_raw.json"

    with open(branded_file, "w", encoding="utf-8") as f:
        json.dump(branded_medicines, f, indent=2, ensure_ascii=False)

    with open(generic_file, "w", encoding="utf-8") as f:
        json.dump(generic_medicines, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated:")
    print(f" -> {len(branded_medicines)} branded medicines in {branded_file}")
    print(f" -> {len(generic_medicines)} generic alternatives in {generic_file}")


if __name__ == "__main__":
    generate_datasets(target_branded_count=3000)