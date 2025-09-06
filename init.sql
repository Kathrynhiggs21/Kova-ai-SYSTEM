-- Kova AI System - Database Initialization
-- Save this as: kova-ai/scripts/init.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schema
CREATE SCHEMA IF NOT EXISTS kova;

-- Set default schema
SET search_path TO kova, public;

-- ================================================
-- Tables
-- ================================================

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(500),
    url VARCHAR(1000),
    owner VARCHAR(255),
    default_branch VARCHAR(100) DEFAULT 'main',
    language VARCHAR(50),
    is_private BOOLEAN DEFAULT FALSE,
    health_score DECIMAL(5,2) DEFAULT 100.00,
    last_scan_at TIMESTAMP,
    scan_interval_minutes INTEGER DEFAULT 60,
    auto_fix_enabled BOOLEAN DEFAULT TRUE,
    webhook_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Errors table
CREATE TABLE IF NOT EXISTS errors (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    line_number INTEGER,
    column_number INTEGER,
    error_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    suggested_fix TEXT,
    confidence DECIMAL(3,2) DEFAULT 0.00,
    is_fixed BOOLEAN DEFAULT FALSE,
    is_ignored BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fixed_at TIMESTAMP,
    fixed_by VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

-- Auto-fixes table
CREATE TABLE IF NOT EXISTS auto_fixes (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    error_id INTEGER REFERENCES errors(id) ON DELETE CASCADE,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    fix_type VARCHAR(50),
    original_code TEXT,
    fixed_code TEXT,
    description TEXT,
    confidence DECIMAL(3,2) DEFAULT 0.00,
    was_applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,
    test_passed BOOLEAN,
    test_results JSONB,
    rollback_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Commands table
CREATE TABLE IF NOT EXISTS ai_commands (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    command_text TEXT NOT NULL,
    intent VARCHAR(50),
    entities JSONB,
    parameters JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    result TEXT,
    confidence DECIMAL(3,2),
    execution_time_ms INTEGER,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Webhooks table
CREATE TABLE IF NOT EXISTS webhooks (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'developer',
    is_active BOOLEAN DEFAULT TRUE,
    api_key VARCHAR(255) UNIQUE,
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(255),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- Indexes
-- ================================================

-- Repository indexes
CREATE INDEX idx_repositories_health_score ON repositories(health_score);
CREATE INDEX idx_repositories_last_scan ON repositories(last_scan_at);
CREATE INDEX idx_repositories_name ON repositories(name);

-- Error indexes
CREATE INDEX idx_errors_severity ON errors(severity);
CREATE INDEX idx_errors_status ON errors(is_fixed);
CREATE INDEX idx_errors_repository ON errors(repository_id);
CREATE INDEX idx_errors_type ON errors(error_type);
CREATE INDEX idx_errors_detected ON errors(detected_at);
CREATE INDEX idx_errors_confidence ON errors(confidence);

-- Auto-fix indexes
CREATE INDEX idx_fixes_applied ON auto_fixes(was_applied);
CREATE INDEX idx_fixes_error ON auto_fixes(error_id);
CREATE INDEX idx_fixes_repository ON auto_fixes(repository_id);

-- AI Command indexes
CREATE INDEX idx_commands_status ON ai_commands(status);
CREATE INDEX idx_commands_created ON ai_commands(created_at);
CREATE INDEX idx_commands_user ON ai_commands(user_id);

-- Webhook indexes
CREATE INDEX idx_webhooks_processed ON webhooks(processed);
CREATE INDEX idx_webhooks_source ON webhooks(source);
CREATE INDEX idx_webhooks_created ON webhooks(created_at);

-- Full-text search indexes
CREATE INDEX idx_errors_message_fts ON errors USING gin(to_tsvector('english', message));
CREATE INDEX idx_commands_text_fts ON ai_commands USING gin(to_tsvector('english', command_text));

-- ================================================
-- Views
-- ================================================

-- Active errors view
CREATE OR REPLACE VIEW active_errors AS
SELECT 
    e.*,
    r.name as repo_name,
    r.full_name as repo_full_name
FROM errors e
JOIN repositories r ON e.repository_id = r.id
WHERE e.is_fixed = FALSE AND e.is_ignored = FALSE;

-- Repository health view
CREATE OR REPLACE VIEW repository_health AS
SELECT 
    r.id,
    r.name,
    r.full_name,
    r.health_score,
    COUNT(CASE WHEN e.severity = 'critical' AND NOT e.is_fixed THEN 1 END) as critical_errors,
    COUNT(CASE WHEN e.severity = 'high' AND NOT e.is_fixed THEN 1 END) as high_errors,
    COUNT(CASE WHEN e.severity = 'medium' AND NOT e.is_fixed THEN 1 END) as medium_errors,
    COUNT(CASE WHEN e.severity = 'low' AND NOT e.is_fixed THEN 1 END) as low_errors,
    COUNT(CASE WHEN e.is_fixed THEN 1 END) as fixed_errors,
    COUNT(e.id) as total_errors,
    CASE 
        WHEN COUNT(e.id) > 0 
        THEN ROUND((COUNT(CASE WHEN e.is_fixed THEN 1 END) * 100.0 / COUNT(e.id))::numeric, 2)
        ELSE 100.00
    END as fix_rate,
    r.last_scan_at,
    r.auto_fix_enabled
FROM repositories r
LEFT JOIN errors e ON r.id = e.repository_id
GROUP BY r.id, r.name, r.full_name, r.health_score, r.last_scan_at, r.auto_fix_enabled;

-- Daily statistics view
CREATE OR REPLACE VIEW daily_statistics AS
SELECT 
    DATE(detected_at) as date,
    COUNT(*) as errors_detected,
    COUNT(CASE WHEN is_fixed THEN 1 END) as errors_fixed,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    AVG(confidence) as avg_confidence
FROM errors
GROUP BY DATE(detected_at);

-- ================================================
-- Functions
-- ================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Calculate repository health score
CREATE OR REPLACE FUNCTION calculate_health_score(repo_id INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    score DECIMAL;
    critical_count INTEGER;
    high_count INTEGER;
    medium_count INTEGER;
    low_count INTEGER;
BEGIN
    SELECT 
        COUNT(CASE WHEN severity = 'critical' AND NOT is_fixed THEN 1 END),
        COUNT(CASE WHEN severity = 'high' AND NOT is_fixed THEN 1 END),
        COUNT(CASE WHEN severity = 'medium' AND NOT is_fixed THEN 1 END),
        COUNT(CASE WHEN severity = 'low' AND NOT is_fixed THEN 1 END)
    INTO critical_count, high_count, medium_count, low_count
    FROM errors
    WHERE repository_id = repo_id;
    
    score := 100.0 - (critical_count * 25) - (high_count * 10) - (medium_count * 5) - (low_count * 2);
    
    IF score < 0 THEN
        score := 0;
    END IF;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- Triggers
-- ================================================

-- Update timestamp triggers
CREATE TRIGGER update_repositories_updated_at
BEFORE UPDATE ON repositories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Update repository health score on error change
CREATE OR REPLACE FUNCTION update_repository_health()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE repositories
    SET health_score = calculate_health_score(NEW.repository_id)
    WHERE id = NEW.repository_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_health_on_error
AFTER INSERT OR UPDATE OR DELETE ON errors
FOR EACH ROW
EXECUTE FUNCTION update_repository_health();

-- ================================================
-- Initial Data
-- ================================================

-- Insert default admin user
INSERT INTO users (email, username, full_name, role, api_key)
VALUES (
    'admin@kova-ai.com',
    'admin',
    'System Administrator',
    'admin',
    encode(gen_random_bytes(32), 'hex')
) ON CONFLICT (email) DO NOTHING;

-- Insert sample repository
INSERT INTO repositories (name, full_name, url, owner, health_score)
VALUES (
    'kova-ai',
    'kova/kova-ai',
    'https://github.com/kova/kova-ai',
    'kova',
    100.00
) ON CONFLICT (name) DO NOTHING;

-- ================================================
-- Permissions
-- ================================================

-- Grant permissions to kova_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA kova TO kova_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA kova TO kova_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA kova TO kova_user;

-- ================================================
-- Statistics
-- ================================================

SELECT 
    'Database initialized successfully!' as message,
    (SELECT COUNT(*) FROM repositories) as repositories_count,
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM errors) as errors_count;