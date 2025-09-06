-- DB schema for KOVA AI Platform
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS errors (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repositories(id),
    message TEXT NOT NULL,
    error_type VARCHAR(100),
    file_path TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auto_fixes (
    id SERIAL PRIMARY KEY,
    error_id INTEGER REFERENCES errors(id),
    fix_description TEXT NOT NULL,
    fix_code TEXT,
    confidence_score DECIMAL(3,2),
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_commands (
    id SERIAL PRIMARY KEY,
    command TEXT NOT NULL,
    response TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_errors_repository_id ON errors(repository_id);
CREATE INDEX IF NOT EXISTS idx_errors_created_at ON errors(created_at);
CREATE INDEX IF NOT EXISTS idx_auto_fixes_error_id ON auto_fixes(error_id);
CREATE INDEX IF NOT EXISTS idx_ai_commands_status ON ai_commands(status);
CREATE INDEX IF NOT EXISTS idx_ai_commands_created_at ON ai_commands(created_at);
