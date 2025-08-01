# 🧪 HR Assistant Pro - Manual Testing Guide

## 📋 Overview
This guide helps you manually test all NLWeb features implemented in your HR Assistant Pro chatbot.

## 🚀 Prerequisites
1. **Django Backend**: Running on `http://localhost:8000`
2. **MCP Server**: Running on `http://localhost:8001`
3. **Frontend**: Running on `http://localhost:3000` or `http://localhost:8080`
4. **Authentication Token**: `d9b2485ccae623570a261316d567acb274ae65cb`

---

## 🔍 Test 1: Natural Language Queries

### Objective
Test if the chatbot understands natural language requests and responds appropriately.

### Test Cases

#### 1.1 Basic Candidate Search
**Query**: `"Find Python developers"`
**Expected**: Should return candidates with Python/developer skills

#### 1.2 Experience-Based Search
**Query**: `"Show me senior engineers"`
**Expected**: Should return candidates with 5+ years experience

#### 1.3 Location-Based Search
**Query**: `"Search for software engineers in New York"`
**Expected**: Should return candidates from specific locations

#### 1.4 Analytics Queries
**Query**: `"How many candidates do we have?"`
**Expected**: Should return total candidate count (501)

#### 1.5 Comprehensive Search
**Query**: `"Show me all candidates"`
**Expected**: Should return paginated list of all candidates

#### 1.6 Skill-Based Search
**Query**: `"Find UI/UX designers"`
**Expected**: Should return candidates with design skills

#### 1.7 AI/ML Search
**Query**: `"Search for AI engineers"`
**Expected**: Should return candidates with AI/ML skills

#### 1.8 Communication Skills
**Query**: `"Find candidates with excellent communication skills"`
**Expected**: Should return candidates with "Excellent" communication skills

#### 1.9 Stage-Based Search
**Query**: `"Show me candidates in screening stage"`
**Expected**: Should return candidates in "Screening" stage

---

## 🔍 Test 2: Vector Search Capabilities

### Objective
Test semantic search and vector database integration.

### Test Cases

#### 2.1 Semantic Search
**Query**: `"Find backend developers"`
**Expected**: Should return candidates with backend/developer roles

#### 2.2 Similar Skills Search
**Query**: `"Find candidates like John Smith"`
**Expected**: Should return candidates with similar profiles

#### 2.3 Technical Skills Search
**Query**: `"Find DevOps engineers"`
**Expected**: Should return candidates with DevOps skills

---

## 🔍 Test 3: MCP Integration

### Objective
Test Model Context Protocol integration and agent discovery.

### Test Cases

#### 3.1 Agent Discovery
**Query**: `"What agents are available?"`
**Expected**: Should list available HR agents

#### 3.2 Tool Usage
**Query**: `"Export all candidates to CSV"`
**Expected**: Should trigger CSV export functionality

#### 3.3 Schema.org Integration
**Query**: `"Show me structured data for candidates"`
**Expected**: Should return Schema.org formatted data

---

## 🔍 Test 4: Multi-Page Data Access

### Objective
Test access to all candidates across pagination.

### Test Cases

#### 4.1 Large Dataset Access
**Query**: `"Show me all 501 candidates"`
**Expected**: Should access all candidates, not just first page

#### 4.2 Search Across Pages
**Query**: `"Find all engineers across all pages"`
**Expected**: Should search through all pages, not just first 15

#### 4.3 Comprehensive Analytics
**Query**: `"What's the average salary of all candidates?"`
**Expected**: Should calculate across all 501 candidates

---

## 🔍 Test 5: Schema.org Integration

### Objective
Test structured data markup for better AI understanding.

### Test Cases

#### 5.1 Candidate Schema
**Query**: `"Show me candidate data in structured format"`
**Expected**: Should return JSON-LD structured data

#### 5.2 Job Post Schema
**Query**: `"Show me job posting structured data"`
**Expected**: Should return JobPosting schema data

---

## 🔍 Test 6: Conversational Workflows

### Objective
Test complex multi-step conversations.

### Test Cases

#### 6.1 Candidate Search Workflow
**Conversation**:
1. `"Find all software engineers"`
2. `"How many do we have?"`
3. `"Show me the ones with 5+ years experience"`

**Expected**: Should maintain context across messages

#### 6.2 Analytics Workflow
**Conversation**:
1. `"What are our hiring metrics?"`
2. `"Show me recent activities"`
3. `"How many candidates are in screening?"`

**Expected**: Should provide comprehensive analytics

#### 6.3 Data Export Workflow
**Conversation**:
1. `"Export all candidates to CSV"`
2. `"Show me job titles"`
3. `"List all cities"`

**Expected**: Should handle multiple data requests

---

## 🔍 Test 7: Advanced Features

### Objective
Test advanced NLWeb capabilities.

### Test Cases

#### 7.1 Vector Database Stats
**Query**: `"Show me vector database statistics"`
**Expected**: Should show Qdrant collection stats

#### 7.2 Semantic Similarity
**Query**: `"Find candidates similar to [specific candidate]"`
**Expected**: Should use vector similarity search

#### 7.3 Multi-Modal Search
**Query**: `"Find candidates with both Python and AWS skills"`
**Expected**: Should combine multiple search criteria

---

## 🎯 Expected Results

### ✅ Success Indicators
- **Natural Language Understanding**: Chatbot understands conversational queries
- **Vector Search**: Returns semantically relevant results
- **Multi-Page Access**: Can access all 501 candidates
- **MCP Integration**: Uses tools and agents properly
- **Schema.org**: Returns structured data
- **Conversational Flow**: Maintains context across messages

### ❌ Failure Indicators
- **Authentication Errors**: 401 responses
- **404 Errors**: Missing endpoints
- **Empty Results**: No candidates found when should be
- **Context Loss**: Forgets previous conversation
- **Tool Failures**: Functions not working

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Authentication Errors
**Problem**: 401 Unauthorized responses
**Solution**: Check if auth token is valid and being passed correctly

#### 2. Empty Results
**Problem**: No candidates returned
**Solution**: Check if Django backend is running and has data

#### 3. Vector Search Not Working
**Problem**: Semantic search returns no results
**Solution**: Check if Qdrant cloud is connected and has embeddings

#### 4. MCP Server Issues
**Problem**: Tool calls failing
**Solution**: Check if MCP server is running on port 8001

---

## 📊 Test Results Template

```
Test Date: _______________
Tester: ________________

✅ PASSED TESTS:
- Natural Language Queries: ___/10
- Vector Search: ___/3  
- MCP Integration: ___/3
- Multi-Page Access: ___/3
- Schema.org: ___/2
- Conversational Workflows: ___/3

❌ FAILED TESTS:
- [List specific failures]

📝 NOTES:
- [Any observations or issues]
```

---

## 🎉 Success Criteria

Your HR Assistant Pro is working correctly when:

1. **Natural Language Queries**: 8/10 or more successful
2. **Vector Search**: All 3 tests pass
3. **MCP Integration**: All 3 tests pass  
4. **Multi-Page Access**: All 3 tests pass
5. **Schema.org**: Both tests pass
6. **Conversational Workflows**: All 3 tests pass

**Overall Success**: 20/24 tests or better (83%+)

---

## 🚀 Ready to Test!

Your HR Assistant Pro chatbot is now ready for comprehensive testing. Use this guide to verify all NLWeb features are working correctly!

**Happy Testing! 🧪✨** 