# ChromaDB Vector Database Service

This directory contains the ChromaDB vector database service configuration for the AI Launchpad.

## Overview

ChromaDB is an open-source embedding database designed for:
- Storing and querying vector embeddings
- Semantic search
- RAG (Retrieval Augmented Generation) applications
- Document similarity matching

## Components

- **README.md** - This file
- Uses official ChromaDB Docker image (no custom Dockerfile needed)

## Enabling ChromaDB

1. **Edit `services.config`** in the project root:
   ```bash
   ENABLE_CHROMA=true
   ```

2. **Rebuild and start:**
   ```bash
   # Windows
   launchpad build-local
   launchpad run-local

   # macOS/Linux
   ./launchpad.sh build-local
   ./launchpad.sh run-local
   ```

## Connecting to ChromaDB

### From within containers (e.g., client or llm-dispatcher):

**Connection Details:**
- Host: `chroma`
- Port: `8000`
- Protocol: HTTP

**Example with ChromaDB Python client:**
```python
import chromadb

# Connect to ChromaDB
client = chromadb.HttpClient(host='chroma', port=8000)

# Create or get a collection
collection = client.get_or_create_collection(name="my_collection")

# Add documents with embeddings
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query the collection
results = collection.query(
    query_texts=["query document"],
    n_results=2
)

print(results)
```

### From your host machine (for debugging):

The ChromaDB HTTP API is exposed on `localhost:8000` during development:

```bash
# Test with curl
curl http://localhost:8000/api/v1/heartbeat

# Or use any HTTP client
```

## Common Use Cases

### 1. Semantic Search

```python
import chromadb

client = chromadb.HttpClient(host='chroma', port=8000)
collection = client.get_or_create_collection(name="documents")

# Add documents (ChromaDB auto-generates embeddings)
collection.add(
    documents=[
        "The cat sat on the mat",
        "The dog played in the garden",
        "Python is a programming language"
    ],
    ids=["doc1", "doc2", "doc3"]
)

# Semantic search
results = collection.query(
    query_texts=["animal on furniture"],
    n_results=1
)
# Returns: "The cat sat on the mat"
```

### 2. RAG (Retrieval Augmented Generation)

```python
import chromadb

# Store knowledge base
client = chromadb.HttpClient(host='chroma', port=8000)
knowledge = client.get_or_create_collection(name="knowledge_base")

# Add documents from your knowledge base
knowledge.add(
    documents=[
        "AI Launchpad supports local and external LLMs",
        "PostgreSQL is available as an optional service",
        "ChromaDB provides vector storage for embeddings"
    ],
    ids=["fact1", "fact2", "fact3"]
)

# Query relevant context
user_question = "What databases are available?"
context = knowledge.query(query_texts=[user_question], n_results=2)

# Use context with LLM
prompt = f"Context: {context['documents']}\n\nQuestion: {user_question}"
# Send prompt to LLM...
```

### 3. Custom Embeddings

```python
import chromadb
from chromadb.utils import embedding_functions

# Use custom embedding function
client = chromadb.HttpClient(host='chroma', port=8000)

# Example with sentence-transformers
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.create_collection(
    name="custom_embeddings",
    embedding_function=sentence_transformer_ef
)

# Add documents (uses custom embeddings)
collection.add(
    documents=["Document 1", "Document 2"],
    ids=["id1", "id2"]
)
```

## Collection Management

```python
import chromadb

client = chromadb.HttpClient(host='chroma', port=8000)

# List all collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")

# Get collection info
collection = client.get_collection(name="my_collection")
print(f"Count: {collection.count()}")

# Delete a collection
client.delete_collection(name="my_collection")
```

## Data Persistence

Collection data is stored in a Docker volume named `chroma_data`. This ensures:
- Data persists across container restarts
- Data survives container removal
- Easy backups via volume management

**To backup data:**
```bash
docker run --rm -v ai-launchpad_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup.tar.gz /data
```

**To restore data:**
```bash
docker run --rm -v ai-launchpad_chroma_data:/data -v $(pwd):/backup alpine tar xzf /backup/chroma_backup.tar.gz -C /
```

## Troubleshooting

### Container won't start
Check logs:
```bash
launchpad logs chroma
```

### Cannot connect from application
1. Verify ChromaDB is running: `launchpad status`
2. Ensure your service is on the `backend` network
3. Use hostname `chroma` not `localhost` from containers
4. Check ChromaDB is healthy: `curl http://localhost:8000/api/v1/heartbeat`

### Reset database
```bash
launchpad stop
docker volume rm ai-launchpad_chroma_data
launchpad run-local
```

## Resource Usage

- **Memory**: ~200-500MB (varies with data size)
- **CPU**: ~0.25-0.5 cores
- **Disk**: Base image ~100MB + data
- **Network**: Connected to `backend` network

## API Documentation

ChromaDB provides a full REST API. Key endpoints:

- `GET /api/v1/heartbeat` - Health check
- `GET /api/v1/collections` - List collections
- `POST /api/v1/collections` - Create collection
- `POST /api/v1/collections/{collection_id}/add` - Add documents
- `POST /api/v1/collections/{collection_id}/query` - Query collection

Full API documentation: https://docs.trychroma.com/

## Performance Tips

1. **Batch operations** - Add multiple documents at once
2. **Index optimization** - ChromaDB handles this automatically
3. **Query limits** - Use `n_results` parameter to limit results
4. **Collection metadata** - Use metadata filters to narrow searches

## Security Considerations

**Current setup:**
- No authentication (suitable for development)
- Only accessible within Docker network
- Port 8000 exposed for development only

**For production:**
- Consider adding authentication
- Remove port exposure in docker-compose.chroma.yml
- Use HTTPS/TLS for external connections
- Implement API key validation

## Advanced Configuration

You can customize ChromaDB behavior via environment variables in `docker-compose.chroma.yml`:

```yaml
environment:
  - IS_PERSISTENT=TRUE
  - ANONYMIZED_TELEMETRY=FALSE
  - CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token.TokenAuthServerProvider
  - CHROMA_SERVER_AUTH_CREDENTIALS=your-secret-token
```

See [ChromaDB documentation](https://docs.trychroma.com/deployment) for all options.

