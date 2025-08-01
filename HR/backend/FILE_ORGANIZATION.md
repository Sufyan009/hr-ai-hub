# HR Assistant Pro - File Organization Guide

## ✅ Current File Structure (All Files Correctly Placed)

### HR/backend/ (Django Backend)
```
HR/backend/
├── accounts/
│   ├── models.py                    # Django models with Schema.org methods
│   ├── serializers.py               # DRF serializers with Schema.org fields
│   ├── views.py                     # Main API views
│   ├── urls.py                      # URL patterns including NLWeb endpoints
│   ├── nlweb_views.py              # Basic NLWeb agent discovery & communication
│   ├── nlweb_vector_views.py       # Vector-enabled NLWeb endpoints
│   ├── admin.py                     # Django admin configuration
│   ├── filters.py                   # API filters
│   └── migrations/                  # Database migrations
├── core/
│   ├── settings.py                  # Django settings
│   ├── urls.py                      # Main URL configuration
│   └── wsgi.py                      # WSGI configuration
├── tests/
│   ├── __init__.py                  # Makes tests a Python package
│   └── test_vector_nlweb.py        # Vector NLWeb integration tests
├── docs/
│   └── VECTOR_NLWEB_README.md      # Vector database documentation
├── vector_db.py                     # Qdrant & Azure OpenAI integration
├── setup_vector_env.py              # Environment setup helper
├── manage.py                        # Django management script
├── requirements.txt                  # Python dependencies
└── .env                             # Environment variables (create this)
```

### HR/mcp_server/ (FastAPI MCP Server)
```
HR/mcp_server/
├── main.py                          # FastAPI server with NLWeb endpoints
├── agent.py                         # LangChain agent with tools
├── tools.py                         # MCP tools including Schema.org
├── requirements.txt                  # Python dependencies
├── test_nlweb_endpoints.py         # NLWeb endpoint tests
├── test_schema_org_final.py        # Schema.org integration tests
├── test_schema_org_auth.py         # Schema.org auth tests
├── test_schema_org_simple.py       # Schema.org simple tests
├── test_schema_org.py              # Schema.org basic tests
├── test_bulk_confirm.py            # Bulk upload tests
├── test_bulk_upload.py             # Bulk upload tests
├── nlweb_enhancements.py           # NLWeb enhancement utilities
└── README.md                       # MCP server documentation
```

### HR/frontend/ (React Frontend)
```
HR/frontend/
├── src/
│   ├── components/                  # React components
│   ├── pages/                       # Page components
│   ├── services/                    # API services
│   └── contexts/                    # React contexts
├── package.json                     # Node.js dependencies
└── vite.config.ts                   # Vite configuration
```

## 🎯 Key Files and Their Purposes

### Backend Core Files
- **`vector_db.py`**: Qdrant vector database integration with Azure OpenAI embeddings
- **`nlweb_vector_views.py`**: Enhanced NLWeb endpoints with vector search capabilities
- **`setup_vector_env.py`**: Helper script for environment configuration
- **`test_vector_nlweb.py`**: Comprehensive tests for vector NLWeb functionality

### MCP Server Files
- **`main.py`**: FastAPI server with chat and NLWeb endpoints
- **`agent.py`**: LangChain agent with Schema.org and vector tools
- **`tools.py`**: MCP tools including Schema.org data fetching

### Documentation
- **`VECTOR_NLWEB_README.md`**: Complete guide for vector database integration
- **`FILE_ORGANIZATION.md`**: This file - current structure overview

## 🚀 Setup Commands

### Backend Setup
```bash
cd HR/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### MCP Server Setup
```bash
cd HR/mcp_server
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd HR/frontend
npm install
npm run dev
```

## 📁 Files That Were Moved/Organized

1. **`nlweb_vector_views.py`**: Moved from `HR/mcp_server/` to `HR/backend/accounts/`
2. **`vector_db.py`**: Moved from `HR/mcp_server/` to `HR/backend/`
3. **`test_vector_nlweb.py`**: Moved from `HR/mcp_server/` to `HR/backend/tests/`
4. **`setup_vector_env.py`**: Moved from `HR/mcp_server/` to `HR/backend/`
5. **`VECTOR_NLWEB_README.md`**: Moved from `HR/mcp_server/` to `HR/backend/docs/`
6. **`tests/__init__.py`**: Created to make tests a proper Python package

## ✅ Verification Checklist

- [x] All Django models have Schema.org methods
- [x] All serializers include Schema.org fields
- [x] NLWeb endpoints are properly configured in URLs
- [x] Vector database integration is complete
- [x] All test files are in correct locations
- [x] Documentation is properly organized
- [x] Import statements are updated
- [x] Environment setup scripts are in place

## 🔧 Next Steps

1. **Configure Environment Variables**: Add Azure OpenAI and Qdrant credentials to `HR/backend/.env`
2. **Start Qdrant Server**: Install and start Qdrant for vector storage
3. **Test Vector Integration**: Run `python test_vector_nlweb.py` to verify functionality
4. **Start All Servers**: Ensure Django backend and MCP server are running

## 🧪 Testing the Organization

To verify everything is working correctly:

```bash
# Test Django backend
cd HR/backend
python manage.py runserver 8000

# Test MCP server
cd HR/mcp_server
python main.py

# Test vector integration
cd HR/backend
python tests/test_vector_nlweb.py
```

All files are now correctly organized and ready for the next phase of development! 