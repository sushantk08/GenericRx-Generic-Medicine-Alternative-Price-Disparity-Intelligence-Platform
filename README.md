# GenericRx: Generic Medicine Alternative & Price Disparity Intelligence Platform

GenericRx is an end-to-end intelligence platform designed to address medicine price disparity in India. It standardizes messy drug salt compositions across pharmaceutical catalogs, maps expensive brand-name medicines to government-approved generic alternatives (such as PMBJP Jan Aushadhi equivalents), and calculates exact monthly and annual prescription savings.

---

## The Problem
In India, patients managing chronic conditions (diabetes, hypertension, cardiovascular health) frequently spend ₹2,000 to ₹6,000 per month on branded medicines. Most are unaware that government-approved generic alternatives contain the exact same active chemical salt and dosage, but cost 60% to 85% less.

* **Prescription Gap**: Doctors routinely prescribe brand names instead of active chemical compositions.
* **Catalog Fragmentation**: Medicine datasets and salt naming conventions vary widely across portals.
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
    (Standardize salt names, extract dosage e.g. "500mg",
     calculate price per tablet/unit)
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
      [ PostgreSQL 16 ]                 [ MongoDB 7 ]
  (Clean Drug Master, Active        (Raw Source JSON,
   Salts, Price-per-unit, GIN        Manufacturer Disclaimers,
   Trigram Search Indexes)           Side-effects text)
             │
             ▼
     [ FastAPI Async API ] ◄── (Sub-50ms Autocomplete Search)
             │
             ▼ (REST API)
    [ Next.js 14 Dashboard ]
   (Search bar, Side-by-Side Comparison Cards, Monthly Savings Calculator)
```

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js 14, React 18, Tailwind CSS | Instant autocomplete search, comparison cards, and interactive savings calculator |
| **Backend API** | FastAPI, Pydantic, SQLAlchemy, Psycopg 3 | Asynchronous REST endpoints, trigram search, and financial calculation engine |
| **Data Pipeline** | Scrapy, Pandas, NumPy, Regex | Web crawling, chemical salt normalization, dosage parsing, and unit pricing |
| **Relational Store** | PostgreSQL 16 | Relational drug master, active salts, foreign-key mappings, and GIN trigram indexes |
| **Document Store** | MongoDB 7 | Raw JSON snapshots, manufacturer notes, and catalog archives |
| **DevOps** | Docker, Docker Compose | Containerized multi-service orchestration |

---

## Key Engineering Solutions

1\. **Regex Salt Normalization**:
   Resolves messy catalog strings (e.g. `Tab. Metformin HCL 500mg` vs `Metformin Hydrochloride 500 MG Tablet IP`) into canonical chemical compounds (`Metformin Hydrochloride`), numeric strengths (`500.0`), and standardized units (`mg`).

2\. **Price-per-Unit Standardization**:
   Normalizes varied packaging formats to calculate like-for-like pricing:
   $$\text{Price per Tablet} = \frac{\text{MRP}}{\text{Pack Size}}$$

3\. **Sub-50ms Trigram Search**:
   Utilizes PostgreSQL's `pg\_trgm` extension with GIN indexing to power typo-tolerant autocomplete search across branded and generic drugs.

4\. **Interactive Prescription Savings Calculator**:
   Computes monthly spend, generic spend, and projected annual savings in ₹ across customizable daily dosage regimens.

---

## Project Structure

```text
generic-rx/
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoints (autocomplete, details, alternatives, calculator)
│   │   ├── core/             # App configuration & CORS settings
│   │   ├── db/               # Database sessions, schema DDL, indexing & seeding scripts
│   │   ├── models/           # SQLAlchemy ORM & Pydantic schemas
│   │   └── main.py           # FastAPI entrypoint
│   ├── tests/                # Automated API integration tests
│   └── Dockerfile
├── data/
│   ├── processed/            # Cleaned CSV datasets
│   └── raw/                  # Scraped raw JSON archives
├── docker-compose.yml        # Orchestrates PostgreSQL, MongoDB, Backend, and Frontend
├── frontend/
│   ├── app/                  # Next.js App Router (layout.jsx, page.jsx, globals.css)
│   ├── components/           # UI components (SearchBar, ComparisonCard, SavingsCalculator)
│   └── Dockerfile
├── pipeline/
│   ├── genericrx\_scraper/    # Scrapy project (spiders, pipelines, settings)
│   ├── tests/                # Unit tests for normalizers and parsers
│   └── transformers/         # Regex salt normalizer, price calculator, and ETL pipeline
└── requirements.txt          # Python dependencies
```

---

## Quickstart Guide

### 1\. Run via Docker Compose (Recommended)

To build and run all services simultaneously:

```bash
docker compose up -d --build
```

Access the services:
* **Frontend UI**: http://localhost:3000
* **Backend API Documentation (Swagger)**: http://localhost:8000/docs
* **PostgreSQL**: `localhost:5433` (DB: `genericrx\_db`)
* **MongoDB**: `localhost:27018`

---

### 2\. Local Development Setup

#### Databases
```bash
docker compose up -d postgres mongo
```

#### Backend Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run ETL and Seed Database
python pipeline/transformers/etl\_pipeline.py
python backend/app/db/seed\_db.py
python backend/app/db/create\_indexes.py

# Start Backend API
uvicorn backend.app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Running Automated Tests

Run the complete test suite across normalization logic and backend API endpoints:

```bash
pytest
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health and readiness status |
| `GET` | `/api/v1/medicines/autocomplete?q={query}` | Fast trigram/prefix medicine search |
| `GET` | `/api/v1/medicines/{id}` | Detailed specifications of a branded medicine |
| `GET` | `/api/v1/medicines/{id}/alternatives` | Generic alternatives and percentage savings |
| `POST`| `/api/v1/calculator/savings` | Monthly and annual prescription savings calculation |
