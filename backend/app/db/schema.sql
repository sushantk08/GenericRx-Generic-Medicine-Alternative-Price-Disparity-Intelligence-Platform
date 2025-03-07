-- Enable UUID extension if needed in future
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostgreSQL Trigram Extension for sub-second autocomplete & fuzzy matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Active Chemical Salts Table
CREATE TABLE IF NOT EXISTS salts (
    id SERIAL PRIMARY KEY,
    salt_name VARCHAR(255) NOT NULL,
    strength_value NUMERIC(10, 2) NOT NULL,
    strength_unit VARCHAR(20) NOT NULL, -- 'mg', 'ml', 'mcg', 'gm'
    dosage_form VARCHAR(50) NOT NULL,   -- 'Tablet', 'Capsule', 'Syrup', 'Injection'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_salt_strength_form UNIQUE (salt_name, strength_value, strength_unit, dosage_form)
);

-- 2. Branded Medicines Table
CREATE TABLE IF NOT EXISTS branded_medicines (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    salt_id INTEGER NOT NULL REFERENCES salts(id) ON DELETE RESTRICT,
    manufacturer VARCHAR(255),
    pack_size INTEGER NOT NULL CHECK (pack_size > 0),
    mrp NUMERIC(10, 2) NOT NULL CHECK (mrp >= 0),
    price_per_unit NUMERIC(10, 4) NOT NULL CHECK (price_per_unit >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Generic Medicines Table (Jan Aushadhi / PMBJP / Other Generic Catalogs)
CREATE TABLE IF NOT EXISTS generic_medicines (
    id SERIAL PRIMARY KEY,
    generic_name VARCHAR(255) NOT NULL,
    salt_id INTEGER NOT NULL REFERENCES salts(id) ON DELETE RESTRICT,
    source VARCHAR(100) DEFAULT 'Jan Aushadhi (PMBJP)',
    pack_size INTEGER NOT NULL CHECK (pack_size > 0),
    mrp NUMERIC(10, 2) NOT NULL CHECK (mrp >= 0),
    price_per_unit NUMERIC(10, 4) NOT NULL CHECK (price_per_unit >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Basic Foreign Key & Lookup Indexes
CREATE INDEX IF NOT EXISTS idx_branded_salt_id ON branded_medicines(salt_id);
CREATE INDEX IF NOT EXISTS idx_generic_salt_id ON generic_medicines(salt_id);
CREATE INDEX IF NOT EXISTS idx_salts_name ON salts(salt_name);

-- GIN Trigram Indexes for fast autocomplete, prefix, and substring search
CREATE INDEX IF NOT EXISTS idx_branded_name_trgm ON branded_medicines USING gin (brand_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_generic_name_trgm ON generic_medicines USING gin (generic_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_salts_name_trgm ON salts USING gin (salt_name gin_trgm_ops);