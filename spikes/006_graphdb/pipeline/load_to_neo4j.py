#!/usr/bin/env python3
"""
Load documents and embeddings to Neo4j
Requires: pip install neo4j
"""

import json
from pathlib import Path
import sys
import os

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: neo4j driver not installed")
    print("Install with: pip install neo4j")
    sys.exit(1)

class Neo4jLoader:
    """Load documents and embeddings to Neo4j."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = None
    
    def connect(self):
        """Test connection to Neo4j."""
        try:
            self.session = self.driver.session(database="neo4j")
            result = self.session.run("RETURN 1")
            result.consume()
            print("✓ Connected to Neo4j")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            print("Make sure Neo4j is running: docker-compose up -d")
            return False
    
    def create_constraints(self):
        """Create database constraints."""
        print("Creating constraints...")
        try:
            self.session.run("""
            CREATE CONSTRAINT document_id IF NOT EXISTS
            FOR (d:Document) REQUIRE d.id IS UNIQUE
            """)
            print("✓ Document constraint created")
        except Exception as e:
            print(f"⊘ Constraint already exists: {e}")
    
    def load_text_documents(self, documents_path: Path):
        """Load text files as documents."""
        print("\nLoading text documents...")
        
        text_files = list(documents_path.glob("*.txt")) + list(documents_path.glob("*.md"))
        text_files = [f for f in text_files if f.name != "README.md"]
        
        if not text_files:
            print("No text files found")
            return 0
        
        count = 0
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_id = f"doc_{text_file.stem}"
                
                self.session.run("""
                MERGE (d:Document {id: $id})
                SET d.title = $title,
                    d.type = $type,
                    d.content = $content,
                    d.size_bytes = $size,
                    d.created = datetime()
                """, 
                id=doc_id,
                title=text_file.stem,
                type=text_file.suffix.lstrip('.'),
                content=content[:10000],  # Store first 10k chars
                size=len(content)
                )
                
                print(f"✓ Loaded {text_file.name}")
                count += 1
            
            except Exception as e:
                print(f"✗ Error loading {text_file.name}: {e}")
        
        return count
    
    def load_embeddings(self, embeddings_path: Path):
        """Load embeddings and create relationships."""
        print("\nLoading embeddings...")
        
        embedding_files = list(embeddings_path.glob("*_embeddings.json"))
        
        if not embedding_files:
            print("No embedding files found")
            return 0
        
        total_chunks = 0
        for embedding_file in embedding_files:
            try:
                with open(embedding_file, 'r', encoding='utf-8') as f:
                    embeddings = json.load(f)
                
                source_name = embedding_file.stem.replace('_embeddings', '')
                doc_id = f"doc_{source_name}"
                
                # Load first few embeddings as samples
                for i, emb_data in enumerate(embeddings[:10]):  # Limit to first 10 for demo
                    chunk_id = emb_data['id']
                    
                    self.session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MERGE (c:Chunk {id: $chunk_id})
                    SET c.text = $text,
                        c.position = $position,
                        c.created = datetime()
                    MERGE (d)-[:CONTAINS]->(c)
                    """,
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    text=emb_data['text'],
                    position=emb_data.get('position', 0)
                    )
                
                print(f"✓ Loaded embeddings from {embedding_file.name} (first 10 chunks)")
                total_chunks += min(10, len(embeddings))
            
            except Exception as e:
                print(f"✗ Error loading {embedding_file.name}: {e}")
        
        return total_chunks
    
    def show_statistics(self):
        """Display database statistics."""
        print("\nDatabase Statistics:")
        
        try:
            # Count documents
            result = self.session.run("MATCH (d:Document) RETURN COUNT(d) as count")
            doc_count = result.single()["count"]
            print(f"  Documents: {doc_count}")
            
            # Count chunks
            result = self.session.run("MATCH (c:Chunk) RETURN COUNT(c) as count")
            chunk_count = result.single()["count"]
            print(f"  Chunks: {chunk_count}")
            
            # Show documents
            result = self.session.run("MATCH (d:Document) RETURN d.title, d.type LIMIT 5")
            print("\n  Latest documents:")
            for record in result:
                print(f"    - {record['d.title']} ({record['d.type']})")
        
        except Exception as e:
            print(f"Error fetching statistics: {e}")
    
    def close(self):
        """Close connection."""
        if self.session:
            self.session.close()
        self.driver.close()

def main():
    """Load documents and embeddings to Neo4j."""
    # Determine paths based on environment (container vs local)
    script_dir = Path(__file__).parent
    
    # Check if running in container (/app/load_to_neo4j.py -> /app/graph_data)
    if (script_dir / "graph_data").exists():
        graph_data_path = script_dir / "graph_data"
    # Check if running locally (pipeline/load_to_neo4j.py -> ../graph_data)
    else:
        graph_data_path = script_dir.parent / "graph_data"
    
    documents_path = graph_data_path / "documents"
    embeddings_path = graph_data_path / "embeddings"
    
    # Connect to Neo4j
    print("=" * 60)
    print("Neo4j Document Loader")
    print("=" * 60)
    
    # Configuration
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "neo4jpassword")
    
    loader = Neo4jLoader(neo4j_uri, neo4j_user, neo4j_password)
    
    if not loader.connect():
        sys.exit(1)
    
    try:
        # Create constraints
        loader.create_constraints()
        
        # Load documents
        doc_count = loader.load_text_documents(documents_path)
        print(f"✓ Loaded {doc_count} documents")
        
        # Load embeddings
        chunk_count = loader.load_embeddings(embeddings_path)
        print(f"✓ Loaded {chunk_count} chunks")
        
        # Show statistics
        loader.show_statistics()
        
        print("\n" + "=" * 60)
        print("✓ Load complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Open Neo4j Browser: http://localhost:7474")
        print("2. Login with neo4j / neo4jpassword")
        print("3. Try this query:")
        print("   MATCH (d:Document)-[:CONTAINS]->(c:Chunk) RETURN d, c LIMIT 5")
        print("\n" + "=" * 60)
    
    finally:
        loader.close()

if __name__ == "__main__":
    main()
