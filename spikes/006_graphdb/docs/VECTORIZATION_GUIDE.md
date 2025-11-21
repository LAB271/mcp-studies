# Vector Database Setup - Vectorization Pipeline Guide

## Current Status

✅ **Documents Added to `vectordb/documents/`:**
- `ps2man.pdf` (1.0 MB) - PlayStation 2 documentation
- `ps3man.pdf` (2.6 MB) - PlayStation 3 documentation
- `ic_datasheets_reference.md` (6.5 KB) - IC reference guide
- `README.md` (718 B) - Documentation index

## Next Steps for Vector Processing

### Option 1: Manual Vector Embedding Processing

**Step 1: Extract Text from Documents**
```bash
# For PDFs, use a PDF extraction tool
# Option A: Using Python with pdfplumber
pip install pdfplumber

# Option B: Using pypdf
pip install pypdf

# Extract and save to text files
python -c "
import pdfplumber
pdf_path = 'spikes/006_vectorDb/vectordb/documents/ps2man.pdf'
with pdfplumber.open(pdf_path) as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    with open('spikes/006_vectorDb/vectordb/documents/ps2man.txt', 'w') as f:
        f.write(text)
"
```

**Step 2: Create Embeddings**
```bash
# Install embedding library (e.g., sentence-transformers)
pip install sentence-transformers

# Create Python script to generate embeddings
cat > spikes/006_vectorDb/vectorize.py << 'EOF'
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Process documents
docs_path = Path('spikes/006_vectorDb/vectordb/documents')
embeddings_path = Path('spikes/006_vectorDb/vectordb/embeddings')

# Example: Create embeddings for IC reference guide
with open(docs_path / 'ic_datasheets_reference.md', 'r') as f:
    text = f.read()

# Split into chunks
chunks = text.split('\n\n')  # Split by paragraph

embeddings_data = []
for i, chunk in enumerate(chunks):
    if chunk.strip():
        embedding = model.encode(chunk)
        embeddings_data.append({
            'id': f'ic_ref_{i}',
            'text': chunk[:200] + '...',  # Store first 200 chars
            'embedding': embedding.tolist(),
            'source': 'ic_datasheets_reference.md'
        })

# Save embeddings
with open(embeddings_path / 'ic_embeddings.json', 'w') as f:
    json.dump(embeddings_data, f, indent=2)

print(f"Created {len(embeddings_data)} embeddings")
EOF

# Run vectorization
python spikes/006_vectorDb/vectorize.py
```

### Option 2: Using Neo4j with Vector Embeddings (Recommended)

**Step 1: Start Neo4j**
```bash
cd spikes/006_vectorDb
docker-compose up -d

# Wait for Neo4j to start (~30 seconds)
sleep 30
```

**Step 2: Connect to Neo4j and Load Documents**
```bash
# Install Neo4j Python driver
pip install neo4j

# Create loader script
cat > spikes/006_vectorDb/load_to_neo4j.py << 'EOF'
from neo4j import GraphDatabase
import json
from pathlib import Path

# Connect to Neo4j
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4jpassword'))

def load_documents(session):
    # Create constraints and indexes
    session.run("""
    CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE
    """)
    
    # Load IC reference guide
    with open('spikes/006_vectorDb/vectordb/documents/ic_datasheets_reference.md', 'r') as f:
        content = f.read()
    
    # Create document node
    session.run("""
    CREATE (d:Document {
        id: 'ic_ref_001',
        title: 'IC Datasheets Reference',
        type: 'markdown',
        content: $content,
        created: datetime()
    })
    """, content=content)
    
    print("Documents loaded to Neo4j")

# Load documents
with driver.session(database="neo4j") as session:
    load_documents(session)

driver.close()
EOF

python spikes/006_vectorDb/load_to_neo4j.py
```

**Step 3: Access Neo4j Browser**
```
Open browser: http://localhost:7474

Login with:
- Username: neo4j
- Password: neo4jpassword

Try Cypher query:
MATCH (d:Document) RETURN d LIMIT 10
```

### Option 3: Docker-based Processing Pipeline

**Step 1: Create Vectorization Container**
```dockerfile
# Create spikes/006_vectorDb/vectorize.Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY vectordb /app/vectordb

RUN pip install --no-cache-dir \
    sentence-transformers \
    pdfplumber \
    neo4j \
    numpy

COPY vectorize.py /app/
CMD ["python", "vectorize.py"]
```

**Step 2: Build and Run**
```bash
cd spikes/006_vectorDb

# Build container
docker build -f vectorize.Dockerfile -t ic-vectorizer .

# Run vectorization
docker run -v $(pwd)/vectordb:/app/vectordb ic-vectorizer
```

## File Organization Guide

### Current Structure
```
spikes/006_vectorDb/vectordb/
├── documents/              # Source files (PDFs, TXT, MD)
│   ├── ps2man.pdf         # PlayStation 2 manual
│   ├── ps3man.pdf         # PlayStation 3 manual
│   └── ic_datasheets_reference.md
└── embeddings/            # Vector embeddings (JSON/Binary)
    └── (empty - to be filled)
```

### After Vectorization
```
spikes/006_vectorDb/vectordb/
├── documents/
│   ├── ps2man.pdf
│   ├── ps3man.pdf
│   ├── ps2man.txt        # Extracted text
│   ├── ps3man.txt        # Extracted text
│   └── ic_datasheets_reference.md
└── embeddings/
    ├── ps2_embeddings.json
    ├── ps3_embeddings.json
    └── ic_embeddings.json
```

## Recommended Workflow

### For Quick Start (5 minutes)
1. Start Neo4j: `docker-compose up -d`
2. Load documents via Python script
3. Query using Cypher in Neo4j Browser

### For Production Setup (30 minutes)
1. Set up document extraction pipeline
2. Create embedding generation with sentence-transformers
3. Load embeddings to Neo4j
4. Create vector indexes for fast similarity search
5. Test semantic search queries

### For Advanced Setup (1-2 hours)
1. Create microservice for document ingestion
2. Set up batch processing pipeline
3. Implement caching layer
4. Add monitoring and logging
5. Set up CI/CD for document updates

## Useful Commands

### Check vectordb folder
```bash
du -sh spikes/006_vectorDb/vectordb/
find spikes/006_vectorDb/vectordb -type f
```

### Neo4j Status
```bash
cd spikes/006_vectorDb
docker-compose ps
docker-compose logs neo4j
```

### Extract from PDF
```bash
# Using pdftotext (if installed)
pdftotext spikes/006_vectorDb/vectordb/documents/ps2man.pdf \
         spikes/006_vectorDb/vectordb/documents/ps2man.txt
```

## Query Examples (Cypher)

**After loading documents to Neo4j:**

```cypher
# Get all documents
MATCH (d:Document) RETURN d.title, d.type

# Create full-text index (for text search)
CREATE FULLTEXT INDEX documents_content IF NOT EXISTS 
FOR (d:Document) ON EACH [d.content]

# Full-text search example
CALL db.index.fulltext.queryNodes("documents_content", "timer") 
YIELD node, score 
RETURN node.title, score ORDER BY score DESC

# Create semantic search with embeddings (requires vector plugin)
# For Neo4j 5.3+:
CREATE VECTOR INDEX document_embeddings 
IF NOT EXISTS FOR (d:Document) 
ON (d.embedding) OPTIONS {indexConfig: {`vector.dimensions`:384}}
```

## Resources

- **Sentence Transformers:** https://www.sbert.net/
- **Neo4j Documentation:** https://neo4j.com/docs/
- **Cypher Query Language:** https://neo4j.com/docs/cypher-manual/
- **Vector Search in Neo4j:** https://neo4j.com/docs/cypher-manual/current/vector-search/

## Questions?

1. **Do you want automatic vectorization on file upload?**
   → Implement file watcher + vectorization service

2. **Do you need semantic search?**
   → Use embedding similarity with vector indexes

3. **How do you want to query the data?**
   → Neo4j Cypher, REST API, or custom MCP interface

Let me know which approach works best for your use case!
