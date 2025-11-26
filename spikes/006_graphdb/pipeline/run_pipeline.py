#!/usr/bin/env python3
"""
Master Pipeline Script - Complete Vectorization Workflow
Runs: Extract PDFs → Generate Embeddings → Load to Neo4j
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class Colors:
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    RESET = "\033[0m"


def print_section(title):
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"→ {title}")
    print(f"{'=' * 60}{Colors.RESET}\n")


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def check_docker():
    """Check if Docker is running."""
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def check_neo4j_ready():
    """Check if Neo4j is ready."""
    try:
        from neo4j import GraphDatabase

        print("    [Neo4j] Attempting connection to bolt://localhost:7687...")
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jpassword"))
        session = driver.session(database="neo4j")
        result = session.run("RETURN 1")
        result.consume()
        session.close()
        driver.close()
        print("    [Neo4j] Connection successful!")
        return True
    except Exception as e:
        print(f"    [Neo4j] Connection failed: {str(e)}")
        return False


def main():
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════════╗")
    print("║         Vector Database Pipeline - Full Execution          ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)

    # Step 0: Check dependencies
    print_section("Step 0: Checking Dependencies")

    dependencies = {"pdfplumber": "pdfplumber", "sentence_transformers": "sentence-transformers", "neo4j": "neo4j"}

    for module, package in dependencies.items():
        try:
            print(f"  Checking {package}...", end=" ", flush=True)
            __import__(module)
            print_success(f"✓ {package} is installed")
        except ImportError:
            print_warning("not installed")
            print(f"  Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"  ✓ {package} installed successfully")
            else:
                print_error(f"  Failed to install {package}")
                print(f"  Error: {result.stderr[:200]}")

    # Step 1: Start Neo4j
    print_section("Step 1: Starting Neo4j")

    print("  Checking Docker daemon...", end=" ", flush=True)
    if not check_docker():
        print_error("Docker is not running")
        print("  Make sure Docker Desktop is running")
        return False
    print_success("Docker is running")

    print("\n  Starting Neo4j container with docker-compose...")
    result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Failed to start Docker containers: {result.stderr[:200]}")
        return False
    print("  ✓ Docker containers started")

    print("\n  Waiting for Neo4j to become ready (checking every 5 seconds)...\n")
    max_attempts = 12  # 60 seconds total
    for attempt in range(max_attempts):
        print(f"    Attempt {attempt + 1}/{max_attempts}...", end=" ", flush=True)
        if check_neo4j_ready():
            print_success("Ready!")
            break
        print("not yet")
        if attempt < max_attempts - 1:
            time.sleep(5)
    else:
        print_error("Neo4j failed to start after 60 seconds")
        print("\n  Troubleshooting:")
        print("    - Check Docker logs: docker-compose logs neo4j")
        print("    - Ensure port 7687 is not in use: lsof -i :7687")
        return False

    # Step 2: Extract PDFs
    print_section("Step 2: Extracting Text from PDFs")
    if not Path("pipeline/extract_pdfs.py").exists():
        print_error("pipeline/extract_pdfs.py not found")
        return False
    print("Running PDF extraction script...\n")
    result = subprocess.run([sys.executable, "pipeline/extract_pdfs.py"], capture_output=False, text=True)
    if result.returncode != 0:
        print_error("PDF extraction failed")
        return False
    print("\n✓ PDF extraction complete")

    # Step 3: Generate Embeddings
    print_section("Step 3: Generating Vector Embeddings")
    if not Path("pipeline/generate_embeddings.py").exists():
        print_error("pipeline/generate_embeddings.py not found")
        return False
    print("Running embedding generation script...")
    print("Note: This may take several minutes depending on document size\n")
    result = subprocess.run([sys.executable, "pipeline/generate_embeddings.py"], capture_output=False, text=True)
    if result.returncode != 0:
        print_error("Embedding generation failed")
        return False
    print("\n✓ Embedding generation complete")

    # Step 4: Load to Neo4j
    print_section("Step 4: Loading Data to Neo4j")
    if not Path("pipeline/load_to_neo4j.py").exists():
        print_error("pipeline/load_to_neo4j.py not found")
        return False
    print("Loading documents and embeddings to Neo4j...\n")
    result = subprocess.run([sys.executable, "pipeline/load_to_neo4j.py"], capture_output=False, text=True)
    if result.returncode != 0:
        print_error("Data loading failed")
        return False
    print("\n✓ Data loading complete")

    # Success!
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════════╗")
    print("║                   ✓ PIPELINE COMPLETE!                     ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    print(f"{Colors.GREEN}All steps completed successfully!{Colors.RESET}\n")
    print("Next steps:")
    print("  1. Open Neo4j Browser: http://localhost:7474")
    print("  2. Login with: neo4j / neo4jpassword")
    print("  3. Run queries in the browser:")
    print("     - View all documents:")
    print("       MATCH (d:Document) RETURN d")
    print("     - View document chunks:")
    print("       MATCH (d:Document)-[:CONTAINS]->(c:Chunk) RETURN d, c")
    print("\nTo stop Neo4j:")
    print("  cd spikes/006_graphdb && docker-compose down\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
