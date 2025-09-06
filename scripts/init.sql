-- Minimal DB init (safe to run if Postgres exists). Extend as needed.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA IF NOT EXISTS kova;
