# Vector Database Documents

This directory contains source files that will be processed for vectorization.

## Purpose
Files placed here will be processed into vector embeddings for semantic search capabilities.

## Supported Formats
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (with additional processing)
- `.json` - JSON documents

## Example Use Cases
- Package descriptions for semantic search
- Delivery route documentation
- Customer communication history
- Location/geographic data

## Processing Pipeline
1. Files are read from this directory
2. Text is chunked into segments
3. Embeddings are generated for each segment
4. Results are stored in the `embeddings/` directory
