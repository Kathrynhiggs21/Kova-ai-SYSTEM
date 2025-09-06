kova-ai/
├── .env.example                          # Environment variables template
├── Dockerfile                            # Container build configuration
├── README.md                             # Project documentation
├── docker-compose.yml                    # Multi-container orchestration
├── requirements.txt                      # Python dependencies
├── setup_kova_system.sh                  # One-shot deployment script
├── appsheet_config.json                  # AppSheet dashboard configuration
├── app/                                  # Main application code
│   ├── main.py                          # FastAPI application entry point
│   ├── api/                             # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py                    # Health check endpoint
│   │   ├── ai_endpoints.py              # AI command endpoints
│   │   ├── scan_endpoints.py            # Repository scanning endpoints
│   │   └── webhooks.py                  # GitHub webhook handlers
│   ├── database/                        # Database models and connections
│   │   ├── __init__.py
│   │   ├── models.py                    # SQLAlchemy models
│   │   └── session.py                   # Database session management
│   ├── core/                            # Core application logic
│   │   └── __init__.py
│   ├── integrations/                    # External service integrations
│   │   └── __init__.py
│   ├── security/                        # Authentication and security
│   │   └── __init__.py
│   ├── tasks/                           # Background task processing
│   │   └── __init__.py
│   └── utils/                           # Utility functions
│       └── __init__.py
├── scripts/                             # Database and utility scripts
│   ├── init.sql                         # Database schema initialization
│   └── quickstart.sh                    # Quick development start script
├── deployment/                          # Deployment configurations
│   ├── nginx/
│   │   └── nginx.conf                   # Reverse proxy configuration
│   └── kubernetes/
│       └── kova-api.yaml                # Kubernetes deployment manifest
├── monitoring/                          # Monitoring and observability
│   ├── prometheus/
│   │   └── prometheus.yml               # Prometheus scrape configuration
│   └── grafana/
│       └── datasources/
│           └── prometheus.yml           # Grafana data source config
└── docs/                                # Documentation
    ├── DEPLOYMENT_CHECKLIST.md         # Step-by-step deployment guide
    └── architecture.md                  # System architecture documentation