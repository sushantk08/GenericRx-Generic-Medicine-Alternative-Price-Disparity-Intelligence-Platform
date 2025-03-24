# GenericRx: Generic Medicine Alternative & Price Disparity Intelligence Platform

GenericRx is an end-to-end intelligence platform designed to address medicine price disparity in India. It standardizes messy drug salt compositions across pharmaceutical catalogs, maps expensive brand-name medicines to government-approved generic alternatives (such as PMBJP Jan Aushadhi equivalents), and calculates exact monthly and annual prescription savings.

---

## The Problem
In India, chronic patients (managing conditions like diabetes, hypertension, and cardiovascular health) spend between ₹2,000 and ₹6,000 every month on branded medicines. Most patients are unaware that government-approved generic alternatives—available under the Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)—contain the exact same active chemical salt, dosage, and efficacy, but cost 60% to 85% less.

* **Prescription Friction**: Doctors routinely write brand names instead of active chemical compositions.
* **Catalog Fragmentation**: Medicine datasets and salt naming conventions vary widely across portals and manufacturers.
* **Packaging Inconsistency**: Comparing a strip of 10 branded tablets to a bottle of 30 generic tablets requires standardized unit pricing.

---

## End-to-End System Architecture

```text
[ Public Medicine Registries & Jan Aushadhi Price Catalogs ]
                             │
                             ▼ (Scrapy Asynchronous Crawlers)
               [ Python Scraping / Ingestion ]
                             │
                             ▼
             [ Pandas Cleaning & Normalization ]
    (FDC compound splitting, salt standardizer, strength parsing,
     release mechanism extraction, price per tablet/unit)
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
      [ PostgreSQL 16 ]                 [ MongoDB 7 ]
  (Clean Drug Master, Active        (Raw Source JSON,
   Salts, Price-per-unit, GIN        Manufacturer Disclaimers,
   Trigram Search Indexes)           Side-effects text)
             │
             ▼
     [ FastAPI Async API ] ◄── (Sub-15ms Trigram Autocomplete Search)
             │
             ▼ (REST API)
    [ Next.js 14 Dashboard ]
   (Debounced Search Bar, Side-by-Side Comparison Cards, Monthly Savings Calculator)
```

---

## Tech Stack

| Layer | Technology | Role & Capabilities |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js 14, React 18, Tailwind CSS | Debounced autocomplete search, side-by-side comparison cards, and interactive prescription savings calculator |
| **Backend API** | FastAPI, Pydantic, SQLAlchemy 2, Psycopg 3 | Asynchronous REST endpoints, GIN trigram search queries, and financial savings calculation engine |
| **Data Pipeline (ETL)** | Scrapy, Pandas, NumPy, Python Regex | Web crawlers, Fixed-Dose Combination (FDC) salt parser, dosage strength extractor, and unit pricing calculator |
| **Relational Store** | PostgreSQL 16 | Relational drug master, active salts, foreign-key mappings, and GIN trigram indexes (`pg_trgm`) |
| **Document Store** | MongoDB 7 | Raw JSON snapshots, manufacturer notes, and unindexed catalog archives |
| **DevOps** | Docker, Docker Compose | Containerized multi-service orchestration |

---

## Key Engineering Solutions

### 1 Fixed-Dose Combination (FDC) & Single-Salt Normalization
* **Compound Delimiter Splitting**: Splits complex formulations using `+`, `/`, `&`, and `and`.
* **Salt Conjugate Cleaning**: Normalizes chemical esters and salt bases (e.g., `Amlodipine Besylate` → `Amlodipine`).
* **Release Mechanism Extraction**: Identifies and standardizes release kinetics (`SR`, `PR`, `ER`, `XR`, `CR`) into formulation metadata.
* **Canonical Alphabetical Sorting**: Ensures order-independent mapping so that `"Telmisartan 40mg + Amlodipine 5mg"` and `"Amlodipine 5mg + Telmisartan 40mg"` map to the exact same canonical salt key.

### 2 Standardized Price-per-Unit Comparison
Eliminates packaging discrepancies (strips of 10, 15, bottles of 30, vials) by normalizing to unit costs:
$$\text{Price per Tablet} = \frac{\text{MRP}}{\text{Pack Size}}$$
This enables like-for-like comparison (e.g. Telma 40 at ₹14.00/tablet vs. Jan Aushadhi generic at ₹1.80/tablet, an **87.14% reduction**).

### 3 Sub-15ms PostgreSQL Trigram Search
* Indexes medicine names with PostgreSQL's `pg_trgm` extension using GIN (Generalized Inverted Index) structures (`idx_branded_name_trgm`).
* Combines prefix matching with fuzzy similarity, allowing the system to handle typos (e.g., `Tlma` → `Telma`, `Augmentn` → `Augmentin`) in 5 to 12 milliseconds.

### 4 Interactive Prescription Savings Calculator
Enables patients to input multi-drug regimens, customize daily dosage frequencies, and instantly project both monthly and annual healthcare savings in ₹.

---

## Project Structure

```text
generic-rx/
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoints: autocomplete, details, alternatives, calculator
│   │   ├── core/             # Configuration & CORS settings
│   │   ├── db/               # Database sessions, schema DDL, indexing & seeding scripts
│   │   ├── models/           # SQLAlchemy ORM models & Pydantic schemas
│   │   └── main.py           # FastAPI entrypoint
│   ├── tests/                # Automated API integration tests & search latency benchmarks
│   └── Dockerfile
├── data/
│   ├── processed/            # Cleaned CSV datasets (salts, branded, generic)
│   └── raw/                  # Scraped and generated raw JSON archives
├── docker-compose.yml        # Multi-service container orchestration
├── frontend/
│   ├── app/                  # Next.js App Router (layout.jsx, page.jsx, globals.css)
│   ├── components/           # SearchBar, ComparisonCard, SavingsCalculator
│   └── Dockerfile
├── pipeline/
│   ├── genericrx_scraper/    # Scrapy project (spiders, pipelines, settings)
│   ├── tests/                # Unit tests for salt normalizers and price calculators
│   └── transformers/         # FDC salt parser, price calculator, dataset generator, and ETL pipeline
└── requirements.txt          # Pinned Python dependencies
```

---

## Quickstart Guide

### 1 Run with Docker Compose (Full Stack)

To build and start all four services (PostgreSQL, MongoDB, FastAPI, and Next.js):

```bash
docker compose up -d --build
```

Endpoints:
* **Frontend Dashboard**: http://localhost:3000
* **API Interactive Docs (Swagger)**: http://localhost:8000/docs
* **PostgreSQL Database**: `localhost:5433` (DB: `genericrx_db`)
* **MongoDB Store**: `localhost:27018`

---

### 2 Local Development & Dataset Seeding

#### Start Database Containers
```bash
docker compose up -d postgres mongo
```

#### Run Data Pipeline & Seed 3,000 Medicines
```bash
# 1 Activate Python virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2 Generate 3,000 medicine catalog dataset
python pipeline/transformers/generate_catalog.py

# 3 Run ETL cleaning and normalization pipeline
python pipeline/transformers/etl_pipeline.py

# 4 Seed PostgreSQL and build GIN trigram indexes
python backend/app/db/seed_db.py
python backend/app/db/create_indexes.py
```

#### Start Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```

#### Start Frontend UI
```bash
cd frontend
npm install
npm run dev
```

---

## Running Automated Tests & Benchmarks

Run the unit tests across normalization logic and API endpoints:
```bash
pytest
```

Run the search latency benchmark across the 3,000-medicine database:
```bash
python backend/tests/benchmark_search.py
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and version |
| `GET` | `/api/v1/medicines/autocomplete?q={query}` | Sub-15ms trigram/prefix medicine search |
| `GET` | `/api/v1/medicines/{id}` | Specifications of a branded medicine |
| `GET` | `/api/v1/medicines/{id}/alternatives` | Exact salt generic equivalents and savings percentage |
| `POST`| `/api/v1/calculator/savings` | Monthly and annual prescription savings calculation |
