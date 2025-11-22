-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Sensors Table (Structured Metadata)
CREATE TABLE sensors (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sensor Readings Table (Time-Series Data)
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(id),
    value DECIMAL(10, 4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for time-series queries
CREATE INDEX idx_readings_sensor_time ON sensor_readings(sensor_id, timestamp DESC);

-- 3. Sensor Knowledge Table (Unstructured Data with Embeddings)
-- We use 384 dimensions for all-MiniLM-L6-v2 model
CREATE TABLE sensor_knowledge (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(id),
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW index for fast similarity search
CREATE INDEX idx_knowledge_embedding ON sensor_knowledge USING hnsw (embedding vector_cosine_ops);

