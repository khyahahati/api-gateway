## Features

- **Routing and Proxying**  
  Routes incoming API requests to the appropriate backend services, abstracting internal service details from external clients.

- **JWT Authentication**  
  Implements JSON Web Token (JWT)-based authentication to ensure only authorized users can access protected endpoints.

- **Rate Limiting**  
  Controls the number of requests a client can make within a specific time window to prevent abuse and ensure fair usage.

- **Logging**  
  Captures structured request and response logs for observability and debugging.

- **Monitoring (Prometheus)**  
  Exposes metrics for Prometheus scraping, enabling monitoring and alerting of gateway performance.

---
## Running the Gateway

1. **Clone the repository:**
   ```bash
   git clone https://github.com/khyahahati/api-gateway
   
2. **Start the API Gateway:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   
3. **Start the dummy backend service (for testing):**
   ```bash
   uvicorn tests.test_routing:app --reload --port 9000

