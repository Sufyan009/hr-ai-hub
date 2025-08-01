# NLWeb Vector Database Integration

## Overview

This module enhances the HR Assistant Pro platform with advanced vector search capabilities using **Qdrant** vector database and **Azure OpenAI Ada-002** embeddings. This integration enables semantic search and AI-enhanced querying of HR data within the NLWeb ecosystem.

## Features

### 🔍 Semantic Search
- **Natural Language Queries**: Search candidates and jobs using natural language
- **Skill-Based Search**: Find candidates by skills, experience, or qualifications
- **Location-Based Search**: Search by city, region, or location preferences
- **Salary Range Search**: Find candidates or jobs within specific salary ranges

### 🤖 AI-Enhanced Capabilities
- **Azure OpenAI Ada-002 Embeddings**: High-quality text embeddings for semantic understanding
- **Vector Similarity Search**: Find similar candidates and job postings
- **Schema.org Integration**: Structured data enhances AI understanding
- **Score-Based Ranking**: Results ranked by semantic similarity scores

### 🌐 NLWeb Integration
- **Enhanced Agent Discovery**: Agents can discover vector search capabilities
- **Vector Query Endpoints**: Direct semantic search through NLWeb protocol
- **Multi-Agent Communication**: Vector search across multiple agents
- **Real-time Indexing**: Dynamic indexing of new data

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HR Assistant  │    │   Azure OpenAI  │    │     Qdrant      │
│      Pro        │◄──►│   Ada-002       │◄──►│   Vector DB     │
│                 │    │   Embeddings    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NLWeb Agent   │    │   Schema.org    │    │   Vector Search │
│   Discovery     │    │   Structured    │    │   Results       │
│   & Query       │    │   Data          │    │   & Ranking     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup

### 1. Environment Variables

Add these variables to your `.env` file in `HR/backend/`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT=text-embedding-ada-002

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # Optional
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Qdrant Server

**Option A: Local Installation**
```bash
pip install qdrant-client
qdrant
```

**Option B: Docker**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Setup Verification

Run the setup script to verify your configuration:

```bash
python setup_vector_env.py
```

## API Endpoints

### Vector Search Endpoints

#### 1. Direct Vector Search
```http
POST /api/nlweb/vector/search/
Content-Type: application/json
Authorization: Token your_auth_token

{
  "query": "Find candidates with Python experience",
  "search_type": "candidates",  // candidates, jobs, all
  "limit": 10,
  "score_threshold": 0.7
}
```

#### 2. Enhanced NLWeb Agent Query
```http
POST /api/nlweb/vector/query/
Content-Type: application/json
Authorization: Token your_auth_token

{
  "query": "Find senior software engineers",
  "agent_id": "hr-assistant-pro",
  "search_type": "semantic",
  "limit": 10,
  "score_threshold": 0.7
}
```

#### 3. Vector Agent Discovery
```http
GET /api/nlweb/vector/discover/
Authorization: Token your_auth_token
```

#### 4. Vector Agent Status
```http
GET /api/nlweb/vector/status/?agent_id=hr-assistant-pro
Authorization: Token your_auth_token
```

#### 5. Data Indexing
```http
POST /api/nlweb/vector/index/
Content-Type: application/json
Authorization: Token your_auth_token

{
  "type": "candidates",  // candidates or jobs
  "items": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      // ... other candidate fields
    }
  ]
}
```

#### 6. Vector Statistics
```http
GET /api/nlweb/vector/stats/
Authorization: Token your_auth_token
```

## Usage Examples

### Python Client Example

```python
import requests

# Configuration
API_BASE = "http://localhost:8000/api"
AUTH_TOKEN = "your_auth_token"
HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"}

# Search for candidates with Python skills
response = requests.post(
    f"{API_BASE}/nlweb/vector/search/",
    headers=HEADERS,
    json={
        "query": "Find candidates with Python programming experience",
        "search_type": "candidates",
        "limit": 5,
        "score_threshold": 0.6
    }
)

if response.status_code == 200:
    results = response.json()
    print(f"Found {results['results_count']} candidates")
    for candidate in results['results']:
        print(f"- {candidate['name']} (Score: {candidate['score']:.3f})")
```

### JavaScript Client Example

```javascript
const searchCandidates = async (query) => {
  const response = await fetch('/api/nlweb/vector/search/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token your_auth_token'
    },
    body: JSON.stringify({
      query: query,
      search_type: 'candidates',
      limit: 10,
      score_threshold: 0.7
    })
  });
  
  const data = await response.json();
  return data.results;
};
```

## Testing

### Run Vector NLWeb Tests

```bash
python tests/test_vector_nlweb.py
```

This will test:
- ✅ Vector agent discovery
- ✅ Semantic search capabilities
- ✅ Enhanced NLWeb querying
- ✅ Vector agent status
- ✅ Data indexing
- ✅ Vector statistics

### Test Individual Components

```bash
# Test vector database setup
python setup_vector_env.py

# Test specific search queries
python -c "
from vector_db import vector_db
results = vector_db.search_candidates('Python developer')
print(f'Found {len(results)} candidates')
"
```

## Vector Database Collections

### Candidates Collection (`hr_candidates`)
- **Vector Dimensions**: 1536 (Ada-002)
- **Distance Metric**: Cosine similarity
- **Payload Fields**:
  - `id`: Candidate ID
  - `name`: Full name
  - `email`: Email address
  - `job_title`: Current job title
  - `stage`: Application stage
  - `salary`: Current salary
  - `experience`: Years of experience
  - `city`: Location
  - `source`: Recruitment source
  - `skills`: Communication skills
  - `notes`: Additional notes
  - `schema_org_data`: Structured data
  - `schema_org_json`: JSON-LD format

### Job Posts Collection (`hr_job_posts`)
- **Vector Dimensions**: 1536 (Ada-002)
- **Distance Metric**: Cosine similarity
- **Payload Fields**:
  - `id`: Job post ID
  - `title`: Job title
  - `company`: Company name
  - `location`: Job location
  - `description`: Job description
  - `requirements`: Job requirements
  - `min_salary`: Minimum salary
  - `max_salary`: Maximum salary
  - `status`: Job status
  - `schema_org_data`: Structured data
  - `schema_org_json`: JSON-LD format

## Performance Optimization

### Indexing Strategy
- **Batch Indexing**: Index multiple items at once
- **Incremental Updates**: Update vectors when data changes
- **Background Processing**: Index in background threads

### Search Optimization
- **Score Thresholds**: Filter low-quality matches
- **Limit Results**: Control result set size
- **Caching**: Cache frequent queries

### Memory Management
- **Collection Segmentation**: Optimize for large datasets
- **Vector Compression**: Reduce memory footprint
- **Cleanup**: Remove outdated vectors

## Troubleshooting

### Common Issues

1. **Qdrant Connection Failed**
   ```bash
   # Check if Qdrant is running
   curl http://localhost:6333/collections
   
   # Start Qdrant if needed
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Azure OpenAI Connection Failed**
   ```bash
   # Verify environment variables
   echo $AZURE_OPENAI_ENDPOINT
   echo $AZURE_OPENAI_API_KEY
   
   # Test connection
   python setup_vector_env.py
   ```

3. **Low Search Quality**
   - Adjust `score_threshold` (try 0.5-0.8)
   - Improve query text quality
   - Check data indexing quality

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Hybrid Search**: Combine vector and keyword search
- **Multi-Modal**: Support for resume PDFs and images
- **Real-time Updates**: Live indexing of data changes
- **Advanced Filtering**: Complex filter combinations
- **Analytics**: Search analytics and insights

### Integration Roadmap
- **External Agents**: Connect with other NLWeb agents
- **Federated Search**: Search across multiple HR systems
- **AI Recommendations**: Smart candidate-job matching
- **Predictive Analytics**: Forecast hiring needs

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure backward compatibility

## License

This module is part of the HR Assistant Pro platform and follows the same licensing terms. 