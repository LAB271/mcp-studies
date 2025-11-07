# Spike: Docker Deployment with SSL and NGINX Gateway

## Learning Objective
**Primary Question:** How do we deploy MCP servers using Docker containers with SSL/TLS encryption and NGINX as a reverse proxy gateway?

**Context:** To run MCP servers in a production-like environment, we need to understand how to:
- Containerize Python-based MCP servers with Docker
- Set up SSL/TLS for secure HTTPS connections
- Use NGINX as a reverse proxy to route traffic to backend services
- Orchestrate multiple containers with Docker Compose
- Manage local development with self-signed certificates

**Success Criteria:**
- MCP server runs successfully in a Docker container
- NGINX gateway routes HTTPS traffic to the MCP server
- SSL certificates work for local development (https://mcp.local)
- HTTP traffic is redirected to HTTPS
- Services can communicate through Docker networking
- Easy start/stop/rebuild workflows via Makefile

## Hypothesis
**We believe that:** Docker Compose with NGINX as a reverse proxy provides a scalable and secure way to deploy MCP servers locally and in production.

**Because:**
- Docker containerization ensures consistent environments across development and production
- NGINX is a battle-tested, high-performance reverse proxy
- SSL/TLS encryption is essential for secure MCP communications
- Docker networking provides isolated, secure service-to-service communication
- This architecture mirrors production deployment patterns

**We'll know we're right when:**
- The MCP server is accessible via `https://mcp.local/main/`
- SSL certificates are validated (self-signed for local development)
- HTTP requests are automatically redirected to HTTPS
- The NGINX gateway successfully proxies requests to the containerized MCP server
- Services remain isolated yet communicate effectively through Docker networks

## Scope & Constraints
- **Time Box:** 2-3 days for initial implementation and testing
- **Out of Scope:** 
  - Production-grade certificate management (Let's Encrypt)
  - Kubernetes or other orchestration platforms
  - Multi-server load balancing
  - Service mesh implementations
- **Dependencies:** 
  - Docker and Docker Compose installed
  - mkcert for local SSL certificate generation
  - Colima (for macOS) or Docker Desktop
  - spikes/002_logging (logging patterns from previous spike)

## Exploration Log

### Initial Setup - Docker Containerization
**Key Activities:**
- Created `Dockerfile` with multi-stage build for Python/uv-based MCP server
- Configured `docker-compose.yml` orchestrating NGINX and MCP server
- Set up Docker networking with custom bridge network (172.28.0.0/16)
- Implemented health checks for service monitoring

**Findings:**
- FastMCP requires `FASTMCP_HOST=0.0.0.0` to bind to all interfaces in container
- Environment variables effectively configure server behavior
- Volume mounts allow live code updates during development

### SSL/TLS Configuration
**Key Activities:**
- Integrated mkcert for local self-signed certificate generation
- Configured NGINX for SSL termination with TLS 1.2/1.3
- Added `/etc/hosts` entry for `mcp.local` domain
- Implemented HTTP to HTTPS redirect

**Findings:**
- Self-signed certificates work seamlessly with mkcert in browsers
- NGINX SSL session caching improves performance
- Certificate paths must be consistent between host and container volumes

### NGINX Gateway Setup
**Key Activities:**
- Configured NGINX as reverse proxy with `/main/` subpath routing
- Implemented upstream backend with connection pooling (keepalive)
- Added security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Set up health check endpoints at `/` and `/health`

**Findings:**
- Path rewriting requires careful handling of trailing slashes
- Docker DNS resolver (127.0.0.11) enables service discovery by name
- Proxy buffering should be disabled for streaming MCP responses
- WebSocket support configured for future SSE/streaming needs

### Makefile Automation
**Key Activities:**
- Created comprehensive Makefile for deployment lifecycle
- Implemented certificate generation automation
- Added log viewing commands for debugging
- Included cleanup and rebuild workflows

**Findings:**
- `make up` handles certificate creation and service startup automatically
- Separate log commands (`logs-nginx`, `logs-app`) aid debugging
- Clean target thoroughly removes all Docker artifacts
- Status command provides quick service health overview

## Key Insights

### ✅ Confirmed
- **Docker + NGINX works well for MCP servers**: The architecture successfully routes HTTPS traffic through NGINX to containerized MCP servers
- **Self-signed certificates with mkcert**: Provides friction-free local development with proper SSL
- **Docker Compose orchestration**: Simplifies multi-service management and networking
- **Environment-based configuration**: Using environment variables makes services configurable without code changes
- **Subpath routing**: NGINX can successfully route `/main/` to different backend services

### ❌ Challenged
- **Health check complexity**: MCP servers don't expose standard health endpoints by default
- **Path rewriting challenges**: Careful attention needed for trailing slashes in proxy configurations
- **Container networking learning curve**: Understanding Docker DNS and networking took iteration
- **Log volume configuration**: Initial setup had issues with proper log directory mounting

### 🤔 Questions Raised
- How do we handle multiple MCP servers behind the same gateway?
- What's the best approach for certificate rotation in production?
- Should we implement service mesh patterns for more complex deployments?
- How do we monitor and alert on service health in production?
- What's the performance overhead of NGINX proxying vs direct connection?

## Recommendation

**Status:** Complete

**Decision:** Integrate - This Docker + NGINX pattern should be our standard for MCP server deployment

**Rationale:**
1. **Production-ready foundation**: The architecture mirrors production deployment patterns
2. **Security by default**: SSL/TLS encryption ensures secure communications
3. **Scalability**: Easy to add more MCP servers behind the gateway
4. **Developer experience**: Makefile automation makes local development straightforward
5. **Observability**: Centralized logging through NGINX and structured application logs
6. **Isolation**: Docker containers provide process and network isolation

**Next Steps:**
1. Add more MCP servers to demonstrate multi-service routing (see 004_logserver)
2. Implement production certificate management (e.g., Let's Encrypt integration)
3. Add monitoring and metrics collection (Prometheus/Grafana)
4. Create deployment templates for cloud providers (AWS ECS, GCP Cloud Run)
5. Document security best practices and hardening guidelines
6. Add automated testing for the deployment pipeline

## Reference Materials

### Code Location
- **Main directory:** `spikes/003_docker/`
- **Key files:**
  - `docker-compose.yml` - Service orchestration
  - `nginx-gateway.conf` - NGINX reverse proxy configuration
  - `Dockerfile` - MCP server container definition
  - `Makefile` - Deployment automation
  - `main_mcp_server.py` - MCP server implementation

### Usage Commands

```bash
# Start the platform (generates certificates, starts services)
make up

# View all logs
make logs

# View specific service logs
make logs-nginx
make logs-app

# Check service status
make status

# Restart services
make restart

# Rebuild and restart (after code changes)
make rebuild

# Stop services
make down

# Complete cleanup (removes containers, volumes, images)
make clean
```

### Access URLs
- **Gateway Root:** https://mcp.local/
- **Gateway Health:** https://mcp.local/health
- **Main MCP Server:** https://mcp.local/main/

### Related Spikes
- **001_demos** - Basic MCP server implementation patterns
- **002_logging** - Structured logging configuration (used in this spike)
- **004_logserver** - Extended version with multiple MCP servers

### External Resources
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NGINX Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [mkcert - Simple Local SSL](https://github.com/FiloSottile/mkcert)
- [FastMCP HTTP Transport](https://github.com/jlowin/fastmcp)
- [Docker Networking](https://docs.docker.com/network/)

### Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                    Docker Host                       │
│                                                      │
│  ┌───────────────────────────────────────────────┐   │
│  │  NGINX Gateway (nginx-gateway)                │   │
│  │  - Port 80 (HTTP → HTTPS redirect)            │   │
│  │  - Port 443 (HTTPS)                           │   │
│  │  - SSL Termination                            │   │
│  │  - Reverse Proxy                              │   │
│  └────────────────┬──────────────────────────────┘   │
│                   │ Docker Network (mcp-network)     │
│                   │ 172.28.0.0/16                    │
│  ┌────────────────▼──────────────────────────────┐   │
│  │  MCP Server (mcp-server)                      │   │
│  │  - Port 8000 (internal)                       │   │
│  │  - FastMCP HTTP transport                     │   │
│  │  - Tools: greet, calculate                    │   │
│  └───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘

External Access:
  https://mcp.local/ → NGINX:443 → mcp-server:8000
```

### Security Features
- **SSL/TLS Encryption**: All traffic encrypted with TLS 1.2/1.3
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **HTTP Redirect**: Automatic HTTP → HTTPS redirect
- **Network Isolation**: Docker bridge network isolates services
- **No Direct Exposure**: MCP server only accessible through gateway

### Performance Optimizations
- **Connection Pooling**: NGINX keepalive connections to backend (32 connections)
- **Gzip Compression**: Enabled for text-based responses
- **Proxy Buffering**: Disabled for streaming responses
- **DNS Caching**: 30-second cache for container DNS lookups
- **SSL Session Cache**: 10MB shared SSL session cache
