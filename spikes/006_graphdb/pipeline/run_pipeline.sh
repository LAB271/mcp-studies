#!/bin/bash

# Master Pipeline Script - Complete Vectorization Workflow
# This script runs the entire pipeline: extract PDFs → generate embeddings → load to Neo4j

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Vector Database Pipeline - Full Execution          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_section() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}→ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Step 0: Check dependencies
print_section "Step 0: Checking Dependencies"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check if pdfplumber is installed
echo "Checking pdfplumber..."
if python3 -c "import pdfplumber" 2>/dev/null; then
    print_success "pdfplumber is installed"
else
    print_warning "pdfplumber not installed - installing now..."
    pip install pdfplumber
    print_success "pdfplumber installed"
fi

# Check if sentence-transformers is installed
echo "Checking sentence-transformers..."
if python3 -c "import sentence_transformers" 2>/dev/null; then
    print_success "sentence-transformers is installed"
else
    print_warning "sentence-transformers not installed - installing now..."
    pip install sentence-transformers
    print_success "sentence-transformers installed"
fi

# Check if neo4j driver is installed
echo "Checking neo4j..."
if python3 -c "import neo4j" 2>/dev/null; then
    print_success "neo4j driver is installed"
else
    print_warning "neo4j driver not installed - installing now..."
    pip install neo4j
    print_success "neo4j driver installed"
fi

echo ""

# Step 1: Start Neo4j
print_section "Step 1: Starting Neo4j"
echo ""

echo "Checking if Docker is running..."
if ! docker info &> /dev/null; then
    print_error "Docker is not running"
    exit 1
fi
print_success "Docker is running"

echo "Starting Neo4j container..."
docker-compose up -d > /dev/null 2>&1

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to start (30 seconds)..."
sleep 30

# Test connection
if timeout 10 python3 -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4jpassword')); session = driver.session(); session.run('RETURN 1'); print('✓ Neo4j is ready')" 2>/dev/null; then
    print_success "Neo4j is ready"
else
    print_error "Neo4j failed to start - check docker-compose logs"
    exit 1
fi

echo ""

# Step 2: Extract PDFs
print_section "Step 2: Extracting Text from PDFs"
echo ""

if [ -f "extract_pdfs.py" ]; then
    python3 extract_pdfs.py
    print_success "PDF extraction complete"
else
    print_error "extract_pdfs.py not found"
    exit 1
fi

echo ""

# Step 3: Generate Embeddings
print_section "Step 3: Generating Vector Embeddings"
echo ""

if [ -f "generate_embeddings.py" ]; then
    python3 generate_embeddings.py
    print_success "Embedding generation complete"
else
    print_error "generate_embeddings.py not found"
    exit 1
fi

echo ""

# Step 4: Load to Neo4j
print_section "Step 4: Loading Data to Neo4j"
echo ""

if [ -f "load_to_neo4j.py" ]; then
    python3 load_to_neo4j.py
    print_success "Data loading complete"
else
    print_error "load_to_neo4j.py not found"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ✓ PIPELINE COMPLETE!                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}All steps completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Open Neo4j Browser: http://localhost:7474"
echo "  2. Login with: neo4j / neo4jpassword"
echo "  3. Run queries:"
echo "     - View all documents: MATCH (d:Document) RETURN d"
echo "     - View document chunks: MATCH (d:Document)-[:CONTAINS]->(c:Chunk) RETURN d, c"
echo ""
echo "To stop Neo4j:"
echo "  cd spikes/006_vectorDb && docker-compose down"
echo ""
