# (Removed)

<!-- File content removed as part of markdown purge -->

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL AI SYSTEMS                              │
│  (Claude, ChatGPT, LangChain Agents, Custom Bots, etc.)                 │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                   HTTP/REST via MCP
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                   FastAPI Web Server (app.py)                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    MCP SERVER LAYER (NEW)                      │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ core/mcp_server.py                                             │   │
│  │  • AgentSangamMCPServer                                        │   │
│  │  • MCPTool (4 PDF tools in standard format)                    │   │
│  │  • MCPResource (resource discovery)                            │   │
│  │                                                                 │   │
│  │ MCP Endpoints:                                                 │   │
│  │  ├─ GET /mcp/info              → Server capabilities          │   │
│  │  ├─ GET /mcp/tools             → Tool discovery               │   │
│  │  ├─ GET /mcp/tools/{name}      → Tool details                 │   │
│  │  ├─ POST /mcp/tools/{name}/call → Tool invocation             │   │
│  │  ├─ GET /mcp/resources         → Resource listing             │   │
│  │  └─ GET /mcp/schema            → OpenAPI spec                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   AGENT LAYER (EXISTING)                        │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ runners/ (6 runners)                                           │   │
│  │  ├─ IngestionRunner    → processes PDF content               │   │
│  │  ├─ SegmenterRunner    → segments documents                   │   │
│  │  ├─ SummarizerRunner   → summarizes sections                  │   │
│  │  ├─ IndexerRunner      → indexes entities                     │   │
│  │  ├─ QARunner           → answers questions                    │   │
│  │  └─ AutoRunner         → context awareness                    │   │
│  │                                                                 │   │
│  │ agents/ (6 LlmAgent instances)                                 │   │
│  │  ├─ ingestion_agent                                           │   │
│  │  ├─ segmenter_agent                                           │   │
│  │  ├─ summarizer_agent                                          │   │
│  │  ├─ indexer_agent                                             │   │
│  │  ├─ qa_agent         ← Uses 3 tools                           │   │
│  │  └─ auto_agent                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    TOOL LAYER (INTEGRATED)                      │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ tools/                                                         │   │
│  │  ├─ agent_tools.py (4 BaseTool implementations)              │   │
│  │  │   ├─ PDFSearchTool                                        │   │
│  │  │   ├─ PDFEntityExtractorTool                               │   │
│  │  │   ├─ PDFSummaryTool                                       │   │
│  │  │   └─ PDFContextRetrievalTool                              │   │
│  │  │                                                             │   │
│  │  ├─ tool_registry.py (Tool discovery)                        │   │
│  │  │   ├─ register_tool()                                      │   │
│  │  │   ├─ get_tool()                                           │   │
│  │  │   └─ generate_openapi_schema()                            │   │
│  │  │                                                             │   │
│  │  └─ mcp_server.py (Standard MCP format)                      │   │
│  │      ├─ Exposes all 4 tools via MCP                          │   │
│  │      └─ Provides schema/discovery                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CORE LAYER (EXISTING)                        │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ core/                                                          │   │
│  │  ├─ config.py         → API key, model, settings             │   │
│  │  ├─ pipeline.py       → Agent pipeline orchestration         │   │
│  │  ├─ sessions.py       → User/PDF session management          │   │
│  │  └─ mcp_server.py     → MCP server implementation            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   APPLICATION LAYER                             │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ routes.py                                                      │   │
│  │  ├─ POST /upload             → Upload PDF                     │   │
│  │  ├─ GET /task_status         → Check processing               │   │
│  │  ├─ GET /sessions            → List PDFs                      │   │
│  │  ├─ POST /ask                → Query agent                    │   │
│  │  ├─ GET /tools/registry      → Tool discovery (existing)      │   │
│  │  ├─ GET /mcp/info            → MCP server info (NEW)         │   │
│  │  ├─ GET /mcp/tools           → MCP tool list (NEW)           │   │
│  │  ├─ POST /mcp/tools/*/call   → Call MCP tool (NEW)           │   │
│  │  └─ ... (3 more MCP endpoints)                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PERSISTENCE LAYER                            │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ In-Memory Stores:                                              │   │
│  │  • global_pdfs             → Uploaded PDF metadata             │   │
│  │  • user_histories          → Chat history                      │   │
│  │  • user_pdf_histories      → Per-PDF chat history             │   │
│  │  • background_tasks        → Processing status                │   │
│  │                                                                 │   │
│  │ File Storage:                                                  │   │
│  │  • uploads/                → Uploaded PDF files                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
                    ▼                                ▼
          ┌──────────────────┐          ┌──────────────────┐
          │  Google Gemini   │          │  Backend Storage │
          │  Model API       │          │  (uploads/)      │
          │  (LLM Calls)     │          │  (sessions)      │
          └──────────────────┘          └──────────────────┘
```

## Data Flow

### 1. PDF Upload & Processing

```
User Upload
    ↓
POST /upload (file)
    ↓
Save to uploads/
    ↓
Create session IDs
    ↓
Background Task (async):
  ├─ Extract text (PyMuPDF)
  ├─ Index content (PDFSearchTool)
  ├─ Run ingestion_runner
  ├─ Run segmenter_runner
  ├─ Run summarizer_runner
  └─ Run indexer_runner
    ↓
Status: uploaded → ingested → indexed
    ↓
GET /task_status/{task_id} for progress
```

### 2. Question Answering with Agent Pipeline

```
User Question
    ↓
POST /ask
    ├─ Retrieve relevant context (PDFContextRetrievalTool)
    ├─ Get conversation history
    └─ Combine context + history
    ↓
Query to Gemini with prompt engineering
    ↓
Generate Answer
    ↓
Store in user_pdf_histories
    ↓
Return response
```

### 3. MCP Tool Discovery & Invocation (NEW)

```
External Agent/Tool
    ↓
GET /mcp/info (server info)
    ↓
GET /mcp/tools (list tools)
    ↓
GET /mcp/tools/{name} (get schema)
    ↓
POST /mcp/tools/{name}/call (invoke)
    │
    ├─ Validate JSON against schema
    ├─ Route to appropriate PDFTool
    ├─ Execute tool (async)
    └─ Return result
    ↓
External Agent uses result
```

## Integration Patterns

### Pattern 1: Direct REST Calls
```python
# External agent makes HTTP calls
requests.get("http://localhost:8000/mcp/tools")
requests.post("http://localhost:8000/mcp/tools/pdf_search/call", json={...})
```

### Pattern 2: MCP Protocol
```
External tool registers Agent Sangam as MCP server
→ Automatically discovers tools
→ Calls tools through MCP interface
```

### Pattern 3: LangChain Integration
```python
# LangChain agent wraps MCP endpoints as Tools
agent = initialize_agent(
    tools=[mcp_tool_1, mcp_tool_2, ...],
    llm=llm,
    agent="zero-shot-react-description"
)
```

### Pattern 4: Agent-to-Agent
```
Agent A (Google ADK)
    ↓
Calls tools via runners
    ↓
Results stored in memory
    ↓
Agent B (External, via MCP)
    ↓
Calls PDF tools via /mcp/tools/*
    ↓
Gets same results
```

## Component Interactions

### Tool Invocation Path

```
External Request
    ↓
routes.py: /mcp/tools/{tool_name}/call
    ↓
Import appropriate PDFTool
    ├─ PDFSearchTool
    ├─ PDFEntityExtractorTool
    ├─ PDFSummaryTool
    └─ PDFContextRetrievalTool
    ↓
Execute tool.run_async()
    ↓
Tool queries internal state:
    • global_pdfs[session_id] → get PDF text
    • Or calls indexing functions
    ↓
Return result
    ↓
Format as MCP response
    ↓
Return to client
```

### Agent Execution Path

```
User Question
    ↓
routes.py: /ask
    ↓
routes.py: call_gemini_direct()
    ├─ Build prompt with context
    ├─ Include chat history
    └─ Include relevant doc excerpts
    ↓
Gemini Model (via genai API)
    ↓
Generate response
    ↓
Store in user_pdf_histories
    ↓
Return to user
```

## Technology Stack

| Layer | Component | Technology |
|-------|-----------|-----------|
| **Framework** | Web Server | FastAPI + Uvicorn |
| **AI** | Language Model | Google Gemini (gemini-2.5-flash-lite) |
| **AI** | Agent Framework | Google ADK (LlmAgent, Runner) |
| **Protocol** | MCP | Model Context Protocol 1.0 |
| **PDF** | Processing | PyMuPDF (fitz) |
| **Storage** | Sessions | In-Memory Python dicts |
| **Storage** | Files | Local filesystem (uploads/) |
| **Config** | Environment | python-dotenv |

## Key Files

### MCP Server Files
- `core/mcp_server.py` - MCP server implementation (350+ lines)
- `routes.py` - MCP endpoints (added ~100 lines)
- `tests/test_mcp_server.py` - MCP tests (450+ lines)
- `docs/MCP_SERVER.md` - MCP documentation (400+ lines)

### Existing Files (Integrated)
- `tools/agent_tools.py` - PDF tools (4 BaseTool implementations)
- `tools/tool_registry.py` - Tool discovery
- `agents/*.py` - 6 LlmAgent instances
- `runners/__init__.py` - Agent runners

### Documentation
- `MCP_INTEGRATION.md` - Quick start guide
- `MCP_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `docs/TOOL_INTEGRATION.md` - Original tool integration
- `docs/MCP_SERVER.md` - MCP specification

## Status Overview

| Component | Status | Quality |
|-----------|--------|---------|
| MCP Server | ✅ Complete | Production-ready |
| MCP Endpoints | ✅ 6 endpoints | Full coverage |
| PDF Tools | ✅ 4 tools | All integrated |
| Agents | ✅ 6 agents | Using tools |
| Tool Registry | ✅ Complete | Discoverable |
| Testing | ✅ 450+ lines | Comprehensive |
| Documentation | ✅ Complete | Detailed |
| Security | ✅ Validated | Input validation |
| Logging | ✅ Integrated | Full tracing |

## Quick Reference

### Start Server
```bash
export GOOGLE_API_KEY="your-key"
python app.py
```

### MCP Endpoints
- `GET /mcp/info` - Server info
- `GET /mcp/tools` - Tool list
- `GET /mcp/tools/{name}` - Tool details
- `POST /mcp/tools/{name}/call` - Execute tool
- `GET /mcp/resources` - Resource list
- `GET /mcp/schema` - OpenAPI schema

### Run Tests
```bash
pytest tests/test_mcp_server.py -v
```

### Example MCP Call
```bash
curl -X POST http://localhost:8000/mcp/tools/pdf_search/call \
  -H "Content-Type: application/json" \
  -d '{"pdf_session_id": "id", "query": "term"}'
```

---

**Complete Agent Sangam Architecture with MCP Server Integration**
