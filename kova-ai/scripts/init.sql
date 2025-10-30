-- Kova AI Platform Database Schema
-- Enhanced schema with multi-repo support and Claude integration

-- Repository Table
CREATE TABLE IF NOT EXISTS repository (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL UNIQUE,
    url TEXT NOT NULL,
    description TEXT,
    default_branch VARCHAR(100) DEFAULT 'main',
    status VARCHAR(50) DEFAULT 'active',
    is_enabled BOOLEAN DEFAULT TRUE,
    repo_type VARCHAR(50),
    sync_priority INTEGER DEFAULT 3,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_repository_name ON repository(name);
CREATE INDEX IF NOT EXISTS idx_repository_full_name ON repository(full_name);
CREATE INDEX IF NOT EXISTS idx_repository_status ON repository(status);

-- Error Table
CREATE TABLE IF NOT EXISTS error (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repository(id) ON DELETE CASCADE,
    error_type VARCHAR(100),
    severity VARCHAR(50),
    message TEXT NOT NULL,
    stack_trace TEXT,
    file_path VARCHAR(500),
    line_number INTEGER,
    context JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_error_created_at ON error(created_at);
CREATE INDEX IF NOT EXISTS idx_error_repository_id ON error(repository_id);
CREATE INDEX IF NOT EXISTS idx_error_type ON error(error_type);
CREATE INDEX IF NOT EXISTS idx_error_resolved ON error(resolved);

-- Sync Log Table
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER NOT NULL REFERENCES repository(id) ON DELETE CASCADE,
    sync_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    items_synced INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    details JSONB,
    claude_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_log_repository_id ON sync_log(repository_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_log_created_at ON sync_log(created_at);

-- Webhook Event Table
CREATE TABLE IF NOT EXISTS webhook_event (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repository(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_action VARCHAR(100),
    github_delivery_id VARCHAR(255) UNIQUE,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    response JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_webhook_event_type ON webhook_event(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_processed ON webhook_event(processed);
CREATE INDEX IF NOT EXISTS idx_webhook_created_at ON webhook_event(created_at);

-- Claude Interaction Table
CREATE TABLE IF NOT EXISTS claude_interaction (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repository(id) ON DELETE CASCADE,
    interaction_type VARCHAR(100),
    prompt TEXT NOT NULL,
    response TEXT,
    model VARCHAR(100),
    tokens_used INTEGER,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claude_interaction_repository_id ON claude_interaction(repository_id);
CREATE INDEX IF NOT EXISTS idx_claude_interaction_type ON claude_interaction(interaction_type);
CREATE INDEX IF NOT EXISTS idx_claude_interaction_created_at ON claude_interaction(created_at);

-- Artifact Table
CREATE TABLE IF NOT EXISTS artifact (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(100),
    content TEXT NOT NULL,
    language VARCHAR(50),
    repository_id INTEGER REFERENCES repository(id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_artifact_name ON artifact(name);
CREATE INDEX IF NOT EXISTS idx_artifact_type ON artifact(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifact_repository_id ON artifact(repository_id);
CREATE INDEX IF NOT EXISTS idx_artifact_is_active ON artifact(is_active);

-- Insert default repositories
INSERT INTO repository (name, full_name, url, description, repo_type, sync_priority)
VALUES
    ('Kova-ai-SYSTEM', 'Kathrynhiggs21/Kova-ai-SYSTEM', 'https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM', 'Main Kova AI system orchestration', 'core', 1),
    ('kova-ai', 'Kathrynhiggs21/kova-ai', 'https://github.com/Kathrynhiggs21/kova-ai', 'Core backend API service', 'core', 2),
    ('kova-ai-site', 'Kathrynhiggs21/kova-ai-site', 'https://github.com/Kathrynhiggs21/kova-ai-site', 'Website and documentation', 'frontend', 3),
    ('kova-ai-mem0', 'Kathrynhiggs21/kova-ai-mem0', 'https://github.com/Kathrynhiggs21/kova-ai-mem0', 'Memory and persistence system', 'service', 2),
    ('kova-ai-docengine', 'Kathrynhiggs21/kova-ai-docengine', 'https://github.com/Kathrynhiggs21/kova-ai-docengine', 'Document processing engine', 'service', 2),
    ('Kova-AI-Scribbles', 'Kathrynhiggs21/Kova-AI-Scribbles', 'https://github.com/Kathrynhiggs21/Kova-AI-Scribbles', 'Experimental features', 'experimental', 5)
ON CONFLICT (full_name) DO NOTHING;
