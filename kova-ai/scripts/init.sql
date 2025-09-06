-- DB schema for KOVA AI Platform
CREATE TABLE IF NOT EXISTS repository (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS error (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_error_created_at ON error(created_at);
