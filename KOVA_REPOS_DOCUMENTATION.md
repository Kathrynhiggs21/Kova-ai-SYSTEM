# Kova AI System - Complete Repository Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Repository Ecosystem](#repository-ecosystem)
3. [Architecture Diagrams](#architecture-diagrams)
4. [Inter-Repository Connections](#inter-repository-connections)
5. [External Integrations](#external-integrations)
6. [Data Flow Documentation](#data-flow-documentation)
7. [API Reference](#api-reference)
8. [Service Dependencies](#service-dependencies)
9. [Configuration Management](#configuration-management)
10. [Security Architecture](#security-architecture)

---

## System Overview

The Kova AI System is a production-grade AI-powered development automation platform that integrates Anthropic's Claude AI with GitHub for intelligent code analysis, multi-repository management, and artifact generation.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Multi-Repository Management** | Coordinates 6 interconnected Kova AI repositories |
| **Claude AI Integration** | Deep integration with Anthropic's Claude API for code analysis |
| **GitHub Webhooks** | Real-time event processing and automated analysis |
| **Artifact Generation** | Automated code, documentation, diagrams, and configs |
| **Async Processing** | Non-blocking webhook and background task processing |

---

## Repository Ecosystem

### All Kova Repositories

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         KOVA AI REPOSITORY ECOSYSTEM                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   ┌─────────────────────┐          ┌─────────────────────┐                │
│   │  KOVA-AI-SYSTEM     │◄────────►│     KOVA-AI         │                │
│   │  (Orchestration)    │          │  (Backend API)      │                │
│   │  Priority: 1        │          │  Priority: 2        │                │
│   └─────────────────────┘          └─────────────────────┘                │
│            │                                │                              │
│            │         ┌──────────────────────┘                              │
│            │         │                                                     │
│            ▼         ▼                                                     │
│   ┌─────────────────────┐          ┌─────────────────────┐                │
│   │  KOVA-AI-SITE       │          │   KOVA-AI-MEM0      │                │
│   │  (Frontend/Web)     │          │  (Memory Service)   │                │
│   │  Priority: 3        │          │  Priority: 2        │                │
│   └─────────────────────┘          └─────────────────────┘                │
│            │                                │                              │
│            │                                │                              │
│            ▼                                ▼                              │
│   ┌─────────────────────┐          ┌─────────────────────┐                │
│   │ KOVA-AI-DOCENGINE   │          │ KOVA-AI-SCRIBBLES   │                │
│   │ (Document Service)  │          │  (Experimental)     │                │
│   │  Priority: 2        │          │  Priority: 5        │                │
│   └─────────────────────┘          └─────────────────────┘                │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Repository Details

#### 1. Kova-ai-SYSTEM (Core Orchestration)
**Priority: 1 | Type: Core | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Central orchestration hub for all Kova repositories |
| **Features** | Docker deployment, monitoring, CI/CD, multi-repo sync |
| **Key Files** | `kova_repos_config.json`, `setup_kova_system.sh`, `docker-compose.yml` |
| **Connections** | Manages sync operations for all other repositories |

**Directory Structure:**
```
Kova-ai-SYSTEM/
├── kova-ai/                    # Embedded backend service
├── kovai-ai/                   # Async Claude bridge
├── deployment_templates/       # Deployment configs
├── scripts/                    # Utility scripts
├── .circleci/                  # CI/CD pipeline
└── kova_repos_config.json      # Central configuration
```

---

#### 2. kova-ai (Backend API Service)
**Priority: 2 | Type: Core | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Main FastAPI backend service with Claude AI integration |
| **Features** | REST API, database ORM, webhook processing, artifact generation |
| **Tech Stack** | FastAPI, SQLAlchemy, PostgreSQL, asyncpg |
| **API Base** | `http://localhost:8000` |

**Module Architecture:**
```
kova-ai/app/
├── api/                        # API endpoints
│   ├── health.py               # Health checks
│   ├── ai_endpoints.py         # Claude AI commands
│   ├── webhooks.py             # GitHub webhook handler
│   ├── multi_repo_endpoints.py # Multi-repo management
│   └── artifacts_endpoints.py  # Artifact generation
├── services/                   # Business logic
│   ├── claude_connector.py     # Claude API client
│   └── multi_repo_sync_service.py  # Sync engine
├── database/                   # Data layer
│   ├── models.py               # SQLAlchemy models
│   └── session.py              # DB connection
├── core/                       # Configuration
├── security/                   # Auth/authorization
└── main.py                     # Application entry point
```

---

#### 3. kova-ai-site (Frontend/Website)
**Priority: 3 | Type: Frontend | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Web interface and documentation portal |
| **Features** | User interface, documentation, dashboard |
| **Connects To** | kova-ai (Backend API) |

---

#### 4. kova-ai-mem0 (Memory Service)
**Priority: 2 | Type: Service | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Memory persistence and context management |
| **Features** | State persistence, conversation history, context storage |
| **Connects To** | kova-ai (for data storage), Claude AI (for context) |

---

#### 5. kova-ai-docengine (Document Processing Service)
**Priority: 2 | Type: Service | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Document processing, PDF generation, templates |
| **Features** | Document generation, PDF export, template engine |
| **Connects To** | kova-ai (API integration), artifacts system |

---

#### 6. Kova-AI-Scribbles (Experimental)
**Priority: 5 | Type: Experimental | Owner: Kathrynhiggs21**

| Component | Description |
|-----------|-------------|
| **Purpose** | Experimental features, prototypes, research |
| **Features** | Sandbox testing, proof-of-concepts |
| **Connects To** | Various (experimental integrations) |

---

## Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           KOVA AI SYSTEM ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │   GitHub    │     │   Claude    │     │  Database   │     │ Prometheus  │   │
│  │    API      │     │    API      │     │ PostgreSQL  │     │  /Grafana   │   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘   │
│         │                   │                   │                   │          │
│         │     EXTERNAL INTEGRATIONS             │                   │          │
│  ═══════╪═══════════════════╪═══════════════════╪═══════════════════╪══════════│
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        FASTAPI APPLICATION                               │   │
│  │                         (kova-ai/main.py)                                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │   │
│  │  │  Health  │ │    AI    │ │ Webhooks │ │Multi-Repo│ │Artifacts │      │   │
│  │  │ Endpoint │ │ Endpoints│ │ Handler  │ │ Endpoints│ │ Endpoints│      │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │   │
│  │       │            │            │            │            │             │   │
│  │       └────────────┴────────────┼────────────┴────────────┘             │   │
│  │                                 │                                        │   │
│  │                    ┌────────────┴────────────┐                           │   │
│  │                    │     SERVICE LAYER       │                           │   │
│  │        ┌───────────┴───────────┬─────────────┴───────────┐              │   │
│  │        │                       │                         │              │   │
│  │  ┌─────┴─────┐          ┌──────┴──────┐          ┌───────┴─────┐        │   │
│  │  │  Claude   │          │  Multi-Repo │          │   Database  │        │   │
│  │  │ Connector │          │ Sync Service│          │   Session   │        │   │
│  │  └───────────┘          └─────────────┘          └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Service Communication Flow

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                        SERVICE COMMUNICATION FLOW                              │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────┐                                                              │
│  │   GitHub    │ ──── Webhooks ────┐                                          │
│  │  Repository │                   │                                          │
│  └─────────────┘                   ▼                                          │
│                           ┌─────────────────┐                                 │
│  ┌─────────────┐         │   Webhook       │                                 │
│  │   User      │ ──API──►│   Handler       │                                 │
│  │  Request    │         │                 │                                 │
│  └─────────────┘         └────────┬────────┘                                 │
│                                   │                                          │
│                     ┌─────────────┼─────────────┐                            │
│                     │             │             │                            │
│                     ▼             ▼             ▼                            │
│              ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│              │  Claude  │  │ Multi-   │  │ Artifact │                        │
│              │ Connector│  │Repo Sync │  │Generator │                        │
│              └────┬─────┘  └────┬─────┘  └────┬─────┘                        │
│                   │             │             │                              │
│         ┌─────────┴─────────────┴─────────────┴─────────┐                    │
│         │                                               │                    │
│         ▼                                               ▼                    │
│  ┌─────────────┐                               ┌─────────────┐               │
│  │  Claude AI  │                               │  PostgreSQL │               │
│  │    API      │                               │  Database   │               │
│  └─────────────┘                               └─────────────┘               │
│                                                                              │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Inter-Repository Connections

### Connection Matrix

| Source Repository | Target Repository | Connection Type | Purpose |
|-------------------|-------------------|-----------------|---------|
| Kova-ai-SYSTEM | kova-ai | Contains/Embeds | Hosts backend service |
| Kova-ai-SYSTEM | All repos | Sync/Manage | Multi-repo orchestration |
| kova-ai | kova-ai-site | API Provider | Backend services |
| kova-ai | kova-ai-mem0 | Data Exchange | Context storage |
| kova-ai | kova-ai-docengine | Service Call | Document generation |
| kova-ai-site | kova-ai | API Consumer | Frontend integration |
| kova-ai-mem0 | kova-ai | Data Provider | Memory retrieval |
| kova-ai-docengine | kova-ai | Service Provider | PDF/doc generation |

### Data Flow Between Repositories

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    INTER-REPOSITORY DATA FLOW                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│      ┌─────────────────────────────────────────────────────────────────┐   │
│      │                    KOVA-AI-SYSTEM                                │   │
│      │   ┌─────────────────────────────────────────────────────────┐   │   │
│      │   │              Multi-Repo Sync Engine                      │   │   │
│      │   │                                                          │   │   │
│      │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │   │
│      │   │  │ Discover │  │  Sync    │  │  Status  │              │   │   │
│      │   │  │  Repos   │  │  Repos   │  │  Track   │              │   │   │
│      │   │  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │   │
│      │   └───────┼─────────────┼─────────────┼──────────────────────┘   │   │
│      └───────────┼─────────────┼─────────────┼──────────────────────────┘   │
│                  │             │             │                              │
│      ┌───────────┴─────────────┴─────────────┴──────────────────────────┐   │
│      │                                                                   │   │
│      ▼                         ▼                         ▼               │   │
│ ┌─────────┐              ┌─────────┐              ┌─────────┐           │   │
│ │kova-ai  │◄────────────►│kova-ai- │◄────────────►│kova-ai- │           │   │
│ │(Backend)│   REST API   │  site   │   Events     │  mem0   │           │   │
│ └────┬────┘              └─────────┘              └────┬────┘           │   │
│      │                                                 │                │   │
│      │              ┌─────────────────────────────────┘                 │   │
│      │              │                                                   │   │
│      ▼              ▼                                                   │   │
│ ┌─────────────────────────────┐                                        │   │
│ │      kova-ai-docengine      │                                        │   │
│ │    (Document Generation)    │                                        │   │
│ └─────────────────────────────┘                                        │   │
│                                                                         │   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## External Integrations

### 1. Claude AI Integration

**Service:** Anthropic Claude API
**Model:** claude-3-sonnet-20240229
**Base URL:** `https://api.anthropic.com/v1/messages`

#### Connection Details

```python
# kova-ai/app/services/claude_connector.py

class ClaudeConnector:
    API_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-3-sonnet-20240229"

    # Headers
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
```

#### Artifact Types Supported

| Type | Description | Use Case |
|------|-------------|----------|
| `CODE` | Source code generation | Generate Python, JavaScript, etc. |
| `DOCUMENT` | Markdown documents | README, documentation |
| `DIAGRAM` | Mermaid diagrams | Architecture diagrams |
| `CONFIG` | Configuration files | JSON, YAML, TOML, INI, XML |
| `DATA` | Structured data | JSON data exports |

#### Integration Flow

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Request   │────►│ ClaudeConnector │────►│  Claude API │
│  (User/App) │     │                 │     │             │
└─────────────┘     └────────┬────────┘     └──────┬──────┘
                             │                     │
                             │◄────────────────────┘
                             │    Response
                             ▼
                    ┌─────────────────┐
                    │ Process Result  │
                    │ - Parse output  │
                    │ - Store artifact│
                    │ - Return to user│
                    └─────────────────┘
```

---

### 2. GitHub Integration

**Service:** GitHub REST API v3
**Authentication:** Personal Access Token (PAT)

#### Webhook Event Processing

```python
# kova-ai/app/api/webhooks.py

SUPPORTED_EVENTS = [
    "push",           # Code pushed to repository
    "pull_request",   # PR opened/closed/merged
    "issues",         # Issue created/updated
    "issue_comment",  # Comment on issue
    "workflow_run"    # CI/CD workflow completed
]
```

#### Security: Webhook Signature Verification

```python
def verify_signature(payload: bytes, signature: str) -> bool:
    """HMAC-SHA256 signature verification"""
    expected = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

#### GitHub API Operations

| Operation | Endpoint | Purpose |
|-----------|----------|---------|
| List Repos | `GET /users/{owner}/repos` | Discover repositories |
| Get Repo | `GET /repos/{owner}/{repo}` | Repository details |
| Get Tree | `GET /repos/{owner}/{repo}/git/trees/{sha}` | File structure |
| Get Contents | `GET /repos/{owner}/{repo}/contents/{path}` | File contents |
| List Commits | `GET /repos/{owner}/{repo}/commits` | Recent commits |

---

### 3. Database Integration

**Database:** PostgreSQL 15
**Driver:** asyncpg
**ORM:** SQLAlchemy (async)

#### Database Models

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐       ┌──────────────────┐                    │
│  │   repositories   │       │      errors      │                    │
│  ├──────────────────┤       ├──────────────────┤                    │
│  │ id (PK)          │       │ id (PK)          │                    │
│  │ name             │       │ repo_id (FK)     │───┐                │
│  │ full_name        │◄──────│ error_type       │   │                │
│  │ description      │       │ message          │   │                │
│  │ url              │       │ severity         │   │                │
│  │ is_active        │       │ resolved         │   │                │
│  │ last_sync        │       │ created_at       │   │                │
│  └──────────────────┘       └──────────────────┘   │                │
│           │                                         │                │
│           │  ┌──────────────────┐                  │                │
│           │  │    sync_logs     │                  │                │
│           │  ├──────────────────┤                  │                │
│           └──│ repo_id (FK)     │◄─────────────────┘                │
│              │ sync_type        │                                    │
│              │ status           │                                    │
│              │ started_at       │                                    │
│              │ completed_at     │                                    │
│              │ details          │                                    │
│              └──────────────────┘                                    │
│                                                                      │
│  ┌──────────────────┐       ┌──────────────────┐                    │
│  │  webhook_events  │       │claude_interactions│                    │
│  ├──────────────────┤       ├──────────────────┤                    │
│  │ id (PK)          │       │ id (PK)          │                    │
│  │ event_type       │       │ prompt           │                    │
│  │ payload          │       │ response         │                    │
│  │ processed        │       │ model            │                    │
│  │ created_at       │       │ tokens_used      │                    │
│  └──────────────────┘       │ created_at       │                    │
│                             └──────────────────┘                    │
│                                                                      │
│  ┌──────────────────┐                                               │
│  │    artifacts     │                                               │
│  ├──────────────────┤                                               │
│  │ id (PK)          │                                               │
│  │ artifact_type    │                                               │
│  │ content          │                                               │
│  │ metadata         │                                               │
│  │ created_at       │                                               │
│  └──────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Documentation

### 1. Webhook Processing Flow

```
┌─────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────┐
│ GitHub  │───►│   Webhook    │───►│   Background   │───►│  Claude  │
│ Event   │    │   Handler    │    │   Processor    │    │   API    │
└─────────┘    └──────┬───────┘    └───────┬────────┘    └────┬─────┘
                      │                    │                   │
                      ▼                    ▼                   │
               ┌──────────────┐    ┌──────────────┐           │
               │   Verify     │    │   Store in   │           │
               │  Signature   │    │   Database   │◄──────────┘
               └──────────────┘    └──────────────┘
```

**Step-by-Step:**
1. GitHub sends webhook event to `/webhooks/github`
2. Handler verifies HMAC-SHA256 signature
3. Event is queued for background processing
4. Background task forwards to Claude for analysis
5. Results are stored in database

### 2. Multi-Repository Sync Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MULTI-REPO SYNC PROCESS                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. Load Config                                                       │
│     ┌──────────────────┐                                             │
│     │kova_repos_config │                                             │
│     │     .json        │                                             │
│     └────────┬─────────┘                                             │
│              │                                                        │
│  2. For Each Repository:                                             │
│              ▼                                                        │
│     ┌──────────────────┐     ┌──────────────────┐                   │
│     │  Fetch from      │────►│  Analyze with    │                   │
│     │  GitHub API      │     │  Claude AI       │                   │
│     └──────────────────┘     └────────┬─────────┘                   │
│                                       │                              │
│  3. Process Results:                  ▼                              │
│     ┌──────────────────┐     ┌──────────────────┐                   │
│     │  Update Status   │◄────│  Store Analysis  │                   │
│     │  in Database     │     │  Results         │                   │
│     └──────────────────┘     └──────────────────┘                   │
│                                                                       │
│  4. Retry Logic (on failure):                                        │
│     └─► Exponential backoff: 2s → 4s → 8s → 16s                     │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 3. Artifact Generation Flow

```
User Request ──► artifacts_endpoints.py ──► claude_connector.py
                        │                          │
                        │                          ▼
                        │                   ┌─────────────┐
                        │                   │ Claude API  │
                        │                   └──────┬──────┘
                        │                          │
                        ▼                          ▼
               ┌─────────────────────────────────────────┐
               │           Store Artifact                 │
               │  - Type: CODE/DOCUMENT/DIAGRAM/CONFIG   │
               │  - Content: Generated output            │
               │  - Metadata: Language, format, etc.     │
               └─────────────────────────────────────────┘
```

---

## API Reference

### Health & Status Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/webhooks/status` | Webhook configuration status |
| `GET` | `/metrics` | Prometheus metrics |

### AI Integration Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ai/command` | Execute AI commands |
| `POST` | `/artifacts/create` | Create any artifact type |
| `POST` | `/artifacts/code/generate` | Generate code |
| `POST` | `/artifacts/code/analyze` | Analyze code for issues |
| `POST` | `/artifacts/document/generate` | Generate documentation |
| `POST` | `/artifacts/diagram/generate` | Generate Mermaid diagrams |
| `POST` | `/artifacts/config/generate` | Generate config files |
| `GET` | `/artifacts/types` | List supported artifact types |

### Multi-Repository Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/multi-repo/status` | Get status of all repos |
| `POST` | `/multi-repo/sync` | Sync all or specific repos |
| `GET` | `/multi-repo/discover` | Auto-discover new repos |
| `POST` | `/multi-repo/add` | Add new repository |
| `GET` | `/multi-repo/list` | List all configured repos |
| `GET` | `/multi-repo/config` | Get full configuration |

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/webhooks/github` | GitHub webhook receiver |

---

## Service Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SERVICE DEPENDENCY GRAPH                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                    ┌─────────────────┐                              │
│                    │   FastAPI App   │                              │
│                    │   (main.py)     │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│           ┌─────────────────┼─────────────────┐                     │
│           │                 │                 │                     │
│           ▼                 ▼                 ▼                     │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐               │
│    │   API    │      │ Services │      │ Database │               │
│    │ Routers  │      │  Layer   │      │  Layer   │               │
│    └────┬─────┘      └────┬─────┘      └────┬─────┘               │
│         │                 │                 │                      │
│         │    ┌────────────┴────────────┐   │                      │
│         │    │                         │   │                      │
│         │    ▼                         ▼   │                      │
│         │ ┌──────────────┐  ┌──────────────┐                      │
│         │ │   Claude     │  │  Multi-Repo  │◄─────────────┐       │
│         │ │  Connector   │  │ Sync Service │              │       │
│         │ └──────┬───────┘  └──────┬───────┘              │       │
│         │        │                 │                      │       │
│         │        │  ┌──────────────┴──────────┐          │       │
│         │        │  │                         │          │       │
│         │        ▼  ▼                         ▼          │       │
│         │  ┌─────────────┐             ┌─────────────┐   │       │
│         │  │ Claude API  │             │ GitHub API  │───┘       │
│         │  │ (External)  │             │ (External)  │           │
│         │  └─────────────┘             └─────────────┘           │
│         │                                                        │
│         └────────────────────────────────────────────────────────│
│                                    │                              │
│                                    ▼                              │
│                            ┌─────────────┐                       │
│                            │ PostgreSQL  │                       │
│                            │  Database   │                       │
│                            └─────────────┘                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Python Dependencies

**Core Framework:**
- `fastapi>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation

**Database:**
- `sqlalchemy>=2.0.0` - ORM
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `alembic>=1.12.0` - Database migrations

**HTTP/API:**
- `httpx>=0.25.0` - Async HTTP client
- `aiohttp>=3.9.0` - Alternative async HTTP

**Monitoring:**
- `prometheus-client>=0.19.0` - Metrics export

---

## Configuration Management

### Central Configuration: `kova_repos_config.json`

```json
{
  "github_owner": "Kathrynhiggs21",
  "repositories": [
    {
      "name": "Kova-ai-SYSTEM",
      "priority": 1,
      "type": "core",
      "features": ["orchestration", "docker", "monitoring"]
    },
    {
      "name": "kova-ai",
      "priority": 2,
      "type": "core",
      "features": ["fastapi", "database", "ai"]
    }
    // ... more repositories
  ],
  "sync_settings": {
    "auto_sync": true,
    "interval_minutes": 30
  },
  "discovery_settings": {
    "auto_discover": true,
    "prefix_filter": "kova-ai"
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API authentication |
| `GITHUB_TOKEN` | Yes | GitHub API authentication |
| `GITHUB_WEBHOOK_SECRET` | Yes | Webhook signature verification |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `POSTGRES_PASSWORD` | Yes | Database password |

### Docker Configuration

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://kova:kova_pass@db:5432/kova
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: kova
      POSTGRES_USER: kova
      POSTGRES_PASSWORD: kova_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## Security Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SECURITY ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  EXTERNAL REQUESTS                                                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                                                              │    │
│  │  GitHub Webhook ──────► HMAC-SHA256 Verification            │    │
│  │                                │                             │    │
│  │                                ▼                             │    │
│  │                         ┌──────────────┐                    │    │
│  │                         │ Valid? ───No─► Reject 401        │    │
│  │                         └──────┬───────┘                    │    │
│  │                                │Yes                         │    │
│  │                                ▼                             │    │
│  │                         Process Event                       │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  OUTBOUND API CALLS                                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                                                              │    │
│  │  Claude API ──────► Bearer Token (ANTHROPIC_API_KEY)        │    │
│  │                                                              │    │
│  │  GitHub API ──────► Token Authentication (GITHUB_TOKEN)     │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  DATABASE ACCESS                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                                                              │    │
│  │  PostgreSQL ──────► Credential-based (user/password)        │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Security Best Practices Implemented

1. **Webhook Verification:** HMAC-SHA256 signature validation
2. **API Key Protection:** Environment variable storage
3. **Database Credentials:** Separate user/password authentication
4. **CORS Configuration:** Configurable origin restrictions
5. **Rate Limiting:** Exponential backoff for external APIs

---

## Deployment Options

### Docker Deployment (Recommended)

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Deployment

```yaml
# kova-ai/deployment/kubernetes/kova-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kova-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kova-api
  template:
    spec:
      containers:
      - name: kova-api
        image: kova-ai:latest
        ports:
        - containerPort: 8000
```

---

## Monitoring & Observability

### Metrics Collection

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  FastAPI    │────►│ Prometheus  │────►│  Grafana    │
│  /metrics   │     │  Scraper    │     │  Dashboard  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Available Metrics

- Request count by endpoint
- Response time distribution
- Error rates
- Database connection pool status
- External API call latency

---

## Summary

The Kova AI System is a comprehensive, production-ready platform that:

- **Orchestrates** 6 interconnected repositories through a central management system
- **Integrates** Claude AI for intelligent code analysis and artifact generation
- **Processes** GitHub webhooks in real-time with secure signature verification
- **Persists** all data in PostgreSQL with async SQLAlchemy
- **Monitors** system health through Prometheus and Grafana
- **Deploys** via Docker Compose or Kubernetes

All repositories work together to provide a seamless AI-powered development experience with automated synchronization, intelligent analysis, and comprehensive documentation generation.
