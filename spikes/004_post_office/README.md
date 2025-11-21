# Spike: Post Office Package Management System

## Learning Objective
**Primary Question:** How can we build a practical MCP server that manages structured CSV data with multiple query tools and demonstrates real-world business logic?

**Context:** Building on previous spikes (stdio transport, logging, Docker deployment), we need to explore how MCP servers handle structured data from external sources (CSV files) and provide multiple interconnected tools that query and analyze this data. This simulates a real-world package delivery management system where multiple delivery drivers need access to their assigned packages.

**Success Criteria:** 
- Successfully load and query package data from CSV file
- Implement multiple tools that provide different views/queries on the same dataset
- Deploy as a containerized MCP server with proper networking
- Demonstrate querying by different dimensions (delivery guy, package ID, label, state)
- Show how tools can aggregate and analyze data (statistics)

## Hypothesis
**We believe that:** An MCP server can effectively manage structured business data (package delivery system) by providing specialized tools for different query patterns, where each tool focuses on a specific use case while operating on a shared dataset.

**Because:** 
- CSV provides a simple, readable format for structured data
- Multiple specialized tools are more user-friendly than generic query interfaces
- FastMCP's tool system naturally maps to business operations
- Docker deployment ensures consistent environment with data files

**We'll know we're right when:** 
- Delivery guys can query their specific package assignments
- Package details are accessible by ID with full sender/receiver information
- Statistics show aggregate views (package count, weight, special labels)
- Label-based and state-based searches work correctly
- The system handles 21 packages across 3 delivery guys reliably

## Scope & Constraints
- **Time Box:** 1-2 days for implementation and testing
- **Out of Scope:** 
  - Database backends (sticking with CSV for simplicity)
  - Package status updates (read-only operations)
  - Authentication/authorization per delivery guy
  - Real-time notifications
  - Package tracking history
- **Dependencies:** 
  - Spike 000 (stdio MCP basics)
  - Spike 002 (clean logging patterns)
  - Spike 003 (Docker deployment architecture)
  - mkcert for SSL certificates
  - Docker/Colima environment

## Exploration Log
### Initial Setup
- Created Post Office domain model with realistic package data
- 21 packages distributed across 3 delivery guys
- Package attributes: ID, label (FRAGILE/STANDARD/URGENT), state (delivered/pending), weight, size, sender/receiver details
- Mix of US and Netherlands addresses for variety
- Split between delivered (9 packages) and pending (12 packages) states

### Tool Design
Implemented 6 specialized tools:
1. **get_packages_for_delivery_guy(delivery_guy: int)** - Primary tool for drivers to see their assignments
2. **get_package_details(package_id: str)** - Detailed lookup for specific packages
3. **get_delivery_guy_stats(delivery_guy: int)** - Aggregate statistics (count, weight, special labels)
4. **get_all_delivery_guys()** - Discovery tool to see all active drivers
5. **search_packages_by_label(label: str)** - Filter by FRAGILE/URGENT/STANDARD
6. **get_packages_by_state(state: str)** - Filter by pending/delivered/in_transit

### Database Layer
- Created `PostOfficeDatabase` class to encapsulate CSV operations
- Singleton pattern for data loading (loads once at startup)
- Query methods mirror tool functions
- Handles type conversions (int for delivery_guy, float for weight)
- Includes error handling for missing files

### Docker Architecture
- Reused proven nginx gateway pattern from spike 003
- Mounted CSV file as read-only volume
- Server runs on internal port 8000
- nginx proxies external traffic
- SSL via mkcert for secure local development
- Logs directed to `/tmp/log/mcp-server-post-office`

## Key Insights
- **✅ Confirmed:** 
  - CSV files work well for small-to-medium structured datasets in MCP servers
  - FastMCP's tool system naturally expresses domain operations
  - Multiple query dimensions (by driver, by ID, by label, by state) provide flexible access patterns
  - Clean separation between database layer and tool layer improves maintainability
  - Docker volumes make data files easily accessible to containers
  - Statistics/aggregation tools complement detail/list tools nicely

- **❌ Challenged:** 
  - CSV requires parsing entire file into memory (acceptable for small datasets)
  - No built-in change detection - would need file watching for updates
  - Type safety requires manual conversion (CSV stores everything as strings)
  - Read-only nature means no ability to update package states through tools

- **🤔 Questions Raised:** 
  - How would this scale to thousands of packages?
  - What's the right approach for write operations (update package state)?
  - Should we add pagination for large result sets?
  - How to handle concurrent access if CSV becomes mutable?
  - Could we expose package data as MCP resources instead of/in addition to tools?

## Recommendation
**Status:** Complete

**Decision:** Integrate as reference implementation for structured data management

**Rationale:** 
This spike successfully demonstrates:
- Clean architecture for data-driven MCP servers
- Multiple query patterns on shared dataset
- Realistic business domain modeling
- Proper Docker deployment with data files
- Balance between specialized and general-purpose tools

The Post Office pattern (CSV + multiple query tools + Docker) provides a solid template for other data management use cases: inventory systems, customer databases, configuration management, etc.

**Next Steps:**
1. Consider extracting the CSV database pattern into a reusable component
2. Explore adding MCP resources to expose package data in addition to tools
3. Investigate write operations - how to safely update CSV from tools
4. Add pagination support for large datasets
5. Consider SQLite backend for more complex queries and transactional updates

## Reference Materials
- **Code Location:** `spikes/004_post_office/`
  - `main_server.py` - FastMCP server with 6 tools
  - `packages.csv` - Sample dataset (21 packages)
  - `docker-compose.yml` - Deployment configuration
  - `Makefile` - Build and management commands
  - `nginx-gateway.conf` - Proxy configuration
  
- **Related Spikes:**
  - Spike 000: stdio MCP server basics
  - Spike 002: Clean logging implementation
  - Spike 003: Docker deployment architecture
  - Spike 005: Log server (next evolution with SQLite)

- **External Resources:**
  - [FastMCP Documentation](https://github.com/jlowin/fastmcp)
  - [MCP Specification](https://modelcontextprotocol.io/)
  - [Docker Compose Best Practices](https://docs.docker.com/compose/production/)

## Usage

### Quick Start
```bash
cd spikes/004_post_office
make up        # Start services (generates SSL certs if needed)
make logs      # View logs
make status    # Check service status
make down      # Stop services
```

### Example Tool Calls
```python
# Get all packages for delivery guy 1
get_packages_for_delivery_guy(delivery_guy=1)

# Get detailed info for specific package
get_package_details(package_id="PKG010")

# Get statistics for delivery guy 2
get_delivery_guy_stats(delivery_guy=2)

# Find all FRAGILE packages
search_packages_by_label(label="FRAGILE")

# Find all pending packages
get_packages_by_state(state="pending")
```

### Testing
```bash
# Test via stdio (requires MCP client)
docker-compose run --rm mcp-server python /app/server.py

# View server logs
make logs-app

# Check package data
docker-compose run --rm mcp-server cat /app/packages.csv
