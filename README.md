````markdown
API Gateway

Overview
This project is an API Gateway built with FastAPI that provides a secure, scalable, and efficient entry point for backend services. It is designed to handle authentication, request routing, rate limiting, logging, and monitoring, making it suitable for modern microservice architectures.

The gateway ensures that only authenticated traffic reaches backend services, while also enforcing traffic control and observability standards.

---

Features

- Routing and Proxying  
  Routes incoming API requests to the appropriate backend services, abstracting internal service details from external clients.

- JWT Authentication  
  Implements JSON Web Token (JWT)-based authentication to ensure only authorized users can access protected endpoints.

- Rate Limiting  
  Controls the number of requests a client can make within a specific time window to prevent abuse and ensure fair usage.

- Logging  
  Captures structured request and response logs for observability and debugging.

- Monitoring (Prometheus)  
  Exposes metrics for Prometheus scraping, enabling monitoring and alerting of gateway performance.

---

Project Structure

project-root/
│
├── .gitignore
├── project_structure.txt
├── pyproject.toml
├── README.md
│
├── scripts/
│   └── generate_token.py        # Utility script to generate JWT tokens
│
├── src/
│   ├── main.py                  # Application entry point
│   │
│   ├── api/                     # API endpoints
│   │   ├── health.py            # Health check endpoint
│   │   ├── metrics.py           # Metrics endpoint
│   │   └── __init__.py
│   │
│   ├── core/                    # Core middleware and logic
│   │   ├── auth.py              # JWT authentication middleware
│   │   ├── logging.py           # Logging middleware
│   │   ├── monitoring.py        # Prometheus monitoring middleware
│   │   ├── rate_limit.py        # Rate limiting middleware
│   │   ├── routing.py           # Routing and proxying logic
│   │   └── __init__.py
│   │
│   └── __pycache__/             # Compiled Python cache files
│
├── tests/
│   └── test_routing.py          # Dummy backend service for testing
│
└── __pycache__/                 # Compiled Python cache files

---

Running the Gateway

Start the API Gateway:

```bash
uvicorn src.main:app --reload --port 8000
```

Start the dummy backend service (for testing):

```bash
uvicorn tests.test_routing:app --reload --port 9000
```

