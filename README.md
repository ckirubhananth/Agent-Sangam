## Agent Sangam

Your local “Google” for PDFs — private, multi‑agent semantic search, chapter summaries, and instant answers from your own documents (MCP/OpenAPI ready).

---
### 1. Name & Inspiration
**Why "Agent Sangam"?**  
"Sangam" is a classical Tamil word meaning an association, academy, or forum where scholars gathered to compose, refine, and transmit literature and knowledge. For thousands of years, historic Sangam assemblies (notably under the Pandya rulers in Madurai) acted as collaborative engines of collective intelligence.  

This project adopts the name to reflect the same spirit in a modern, technical context:
- **Multi-agent collaboration** parallels ancient scholars contributing complementary expertise.
- **Document ingestion and indexing** mirrors compiling manuscripts and preserving textual heritage.
- **Contextual retrieval and QA** reflect scholarly commentary and clarification.
- **Open protocols (MCP / OpenAPI)** embody openness and accessibility of a shared knowledge forum.

Thus, "Agent Sangam" symbolizes a digital convergence of autonomous reasoning components forming a living knowledge commons—grounded in cultural heritage while enabling contemporary AI-driven document intelligence.

---
### 2. Problem
People often have hundreds of PDFs spanning thousands of pages. Analyzing them is slow and error‑prone, and true semantic search inside documents is hard. Students keep textbooks as soft copies; when they have a doubt, locating the exact passage for clarification is tedious. The web can answer concepts, but “googling inside the PDF” is not easy.

We’re building a solution to act as a local document googler, analyzer, summarizer, and learning partner. You can ask things like “Summarize Chapter 3” to get concise study notes and exam‑ready explanations quickly.

---
### 3. Solution Overview
Agent Sangam implements a production‑ready FastAPI service with:
- Multi-agent runners (ingestion, segmentation, summarization, indexing, QA, auto-context)
- Four standardized PDF tools exposed internally and externally (search, entities, summary, contextual retrieval)
- Model Context Protocol (MCP) server endpoints for tool discovery & invocation
- OpenAPI generator producing function-call schemas for external LLM orchestration
- Session + in-memory state management for per-PDF and per-user histories
- Asynchronous background processing pipeline for ingestion & indexing

#### Value
- Focused answers fast: semantic retrieval and chapter-level summaries reduce time spent skimming large PDFs.
- Clarification when it matters: ask questions (e.g., “Summarize Chapter 3”) and get concise, exam‑ready notes.
- Keep documents local: PDFs stay on your machine; only model calls go to Gemini as configured.
- Interoperable by design: MCP and OpenAPI make tools discoverable and callable from external agents.
- Extensible toolkit: add new tools (e.g., web search) without changing the core pipeline.
- Cost-aware: retrieves only relevant context before LLM calls, minimizing tokens.

#### Core Concept & Value

### Implementation Highlights
- Architecture: layered design (MCP/OpenAPI → Agents → Tools → Core → Storage) with clear boundaries and single‑purpose modules.
- Code quality: cohesive modules (`core/mcp_server.py`, `core/openapi_generator.py`, `routes.py`, `agents/*`, `tools/*`, `core/sessions.py`) and consistent request/response schemas.
- AI integration: Google Gemini used via orchestrated agents; tools retrieve minimal, relevant context before LLM calls to reduce tokens.
- Async pipeline: background ingestion/indexing for large PDFs; interactive endpoints remain responsive while processing continues.
- Interoperability: MCP endpoints for tool discovery/invocation; OpenAPI generator emits function‑style tool schemas for external agents.
- Validation & safety: Pydantic request models and schema checks; environment‑based configuration in `core/config.py`.
- Extensibility: add tools via `tools/agent_tools.py` + `tool_registry`; expose automatically through MCP/OpenAPI without core rewrites.

---
### 4. Key Features
- Multi-agent orchestration over document lifecycle
- MCP-compliant tool interface (/mcp/*)
- Formal OpenAPI tool schemas (/openapi/*)
- Modular tool registry for dynamic discovery
- Context-aware QA over stored PDF sessions
- Simple, extensible architecture ready for added tools (search web, code exec, etc.)

---
### 5. High-Level Architecture
```
External LLMs / Agent Frameworks / Tools
            │  (HTTP / MCP / OpenAPI)
            ▼
        FastAPI Service (app.py)
  ┌─────────────────────────────────────────┐
  │  MCP Layer (core/mcp_server.py)         │
  │   • Tool & resource discovery           │
  │   • Invocation routing                  │
  ├─────────────────────────────────────────┤
  │  OpenAPI Layer (core/openapi_generator) │
  │   • Function-style schemas              │
  ├─────────────────────────────────────────┤
  │  Agent Layer (agents/*.py)              │
  │   • 6 LlmAgents + runners               │
  ├─────────────────────────────────────────┤
  │  Tool Layer (tools/agent_tools.py)      │
  │   • PDFSearch / Entities / Summary /    │
  │     ContextRetrieval                    │
  ├─────────────────────────────────────────┤
  │  Core (core/pipeline.py, sessions.py)   │
  │   • State, orchestration                │
  ├─────────────────────────────────────────┤
  │  Persistence (in-memory + uploads/)     │
  └─────────────────────────────────────────┘
```

---
### 6. Component Breakdown
| Layer | Purpose | Representative Files |
|-------|---------|----------------------|
| MCP Server | Standard tool exposure | core/mcp_server.py, routes.py |
| OpenAPI | Tool schema generation | core/openapi_generator.py |
| Agents | Task-specific logic | agents/*.py, runners/ |
| Tools | PDF operations | tools/agent_tools.py, tool_registry.py |
| Core | Sessions & pipeline | core/sessions.py, core/pipeline.py |
| Storage | Uploaded content | uploads/ |

---
### 7. Data Flow (Upload → QA)
```
User Upload → /upload → File saved → Session created
  → Background task: extract text, segment, summarize, index
    → Status tracked (task_status) → Ready for queries
User Question → /ask → Context retrieval tool → Gemini prompt → Answer stored & returned
```

---
### 8. PDF Tools
| Tool | Endpoint (MCP call path) | Purpose | Params |
|------|--------------------------|---------|--------|
| pdf_search | /mcp/tools/pdf_search/call | Keyword search in PDF text | pdf_session_id, query, max_results |
| extract_entities | /mcp/tools/extract_entities/call | Named entity extraction | pdf_session_id |
| pdf_summary | /mcp/tools/pdf_summary/call | Global summary | pdf_session_id |
| retrieve_context | /mcp/tools/retrieve_context/call | Context spans for a question | pdf_session_id, question |

OpenAPI tool definitions accessible via `/openapi/tools` and `/openapi/tools/{name}`.

---
### 9. MCP Endpoints
```
GET  /mcp/info                → Server capabilities
GET  /mcp/tools               → List MCP tools
GET  /mcp/tools/{name}        → Tool schema
POST /mcp/tools/{name}/call   → Invoke tool
GET  /mcp/resources           → Resource listing (extensible)
GET  /mcp/schema              → Combined OpenAPI spec
```

---
### 10. OpenAPI Endpoints
```
GET /openapi/spec        → Full spec (generated)
GET /openapi/tools       → All tool definitions
GET /openapi/tools/{t}   → Single tool schema
GET /openapi/json        → Raw JSON export
POST /openapi/validate   → Validate parameters (future extensibility)
```

---
### 11. Setup Instructions
Prerequisites: Python 3.10+, valid Google Gemini API key.

1. Clone repository
```
git clone <your-fork-or-origin> AgentSangam
cd AgentSangam
```
2. Create virtual environment (recommended)
```
python -m venv .venv
./.venv/Scripts/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Set environment variables (PowerShell example)
```
$env:GOOGLE_API_KEY="YOUR_KEY"
$env:GOOGLE_PROJECT = "YOUR_PROJECT_NAME"
$env:GOOGLE_LOCATION = "YOUR_LOCATION"  # e.g. us-central1
```
5. Run application (simple)
```
python app.py
```
6. (Optional) Run with uvicorn explicitly
```
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---
### 12. Basic Usage

Web Application URL:
```
http://localhost:8000/static/index.html
```

Upload a PDF:
```
curl -F "file=@sample.pdf" http://localhost:8000/upload
```
Check task status:
```
curl http://localhost:8000/task_status/<task_id>
```
Ask a question:
```
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"pdf_session_id":"SESSION","question":"What is the summary?"}'
```
List tools (MCP):
```
curl http://localhost:8000/mcp/tools
```
Invoke pdf_search tool:
```
curl -X POST http://localhost:8000/mcp/tools/pdf_search/call -H "Content-Type: application/json" -d '{"pdf_session_id":"SESSION","query":"term","max_results":5}'
```
Retrieve OpenAPI tool schema:
```
curl http://localhost:8000/openapi/tools/pdf_search
```

---
### 13. Integration Examples
Python (requests):
```python
import requests
BASE = "http://localhost:8000"
tools = requests.get(f"{BASE}/mcp/tools").json()["tools"]
resp = requests.post(f"{BASE}/mcp/tools/pdf_search/call", json={
    "pdf_session_id": "SESSION", "query": "contract", "max_results": 3
}).json()
print(resp)
```

LangChain pseudo-tool wrapper:
```python
from langchain.tools import Tool
import requests

def pdf_search_wrapper(pdf_session_id: str, query: str, max_results: int = 5):
    return requests.post("http://localhost:8000/mcp/tools/pdf_search/call", json={
        "pdf_session_id": pdf_session_id, "query": query, "max_results": max_results
    }).json()

pdf_search_tool = Tool(
    name="pdf_search",
    func=lambda q: pdf_search_wrapper("SESSION", q),
    description="Search PDF content by keyword"
)
```

---
### 14. Error Handling & Validation
- Pydantic models ensure incoming payload structure.
- Tool parameter schemas enforce required arguments.
- Background task status prevents premature querying.

---
### 15. Extensibility Guidelines
Add a new tool:
1. Implement a `BaseTool` subclass in `tools/agent_tools.py`.
2. Register via `tool_registry.register_tool()`.
3. Expose through MCP server (auto-picked if added to initialization list).
4. Extend OpenAPI generator if custom parameter typing needed.

---
### 16. Future Roadmap (Not Yet Implemented)
- Web search / code execution tools
- Pause/resume agent lifecycle controls
- Long-term vector memory store
- Context compaction strategies
- Structured metrics + tracing (Observability)
- Automatic evaluation harness
- Containerized deployment (Docker/K8s)

---
### 17. ASCII Detailed Flow
```
[Upload] -> store file -> create session -> background pipeline
    (extract -> segment -> summarize -> index entities)
        ↓
    ready state

[Question] -> retrieve_context tool -> assemble prompt -> LLM (Gemini)
        ↓
    answer -> store history -> return response

MCP / OpenAPI external calls -> tool schema discovery -> invocation -> structured result
```

---
### 18. Security & Notes
- Requires valid API key for Gemini; do not commit secrets.
- All processing currently in-memory; sensitive deployments should add persistence & access control.

---
### 19. Repository Structure (Excerpt)
```
app.py
core/
  config.py, pipeline.py, sessions.py, mcp_server.py, openapi_generator.py
agents/ (qa_agent.py, ingestion_agent.py, ...)
tools/ (agent_tools.py, tool_registry.py)
uploads/ (stored PDFs)
static/ (index.html)
routes.py (HTTP endpoints)
```

---
### 20. Quick Start Commands (PowerShell)
```
python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
$env:GOOGLE_API_KEY="YOUR_KEY"
python app.py
```

---
### 21. Support / Contribution
Open to extension via new tools & agents. Focus on keeping schemas stable for external orchestrators.

---
### 22. License / Usage
Internal development artifact; add license as needed before external distribution.

---
### 23. Status
Core MCP + OpenAPI + multi-agent pipeline COMPLETE. Higher-order observability & memory features pending.

---
Enjoy building with Agent Sangam.

---
### 24. Bonus Points (Tooling, Model Use, Deployment, Video)
This project includes several optional extras that map to bonus credit:

- Tooling: MCP + OpenAPI surfaces, dynamic tool registry (`tools/tool_registry.py`), and formal tool schemas. Try:
    - `GET /mcp/tools`, `GET /openapi/tools/{name}`, `POST /mcp/tools/pdf_search/call`.
- Model Use: Google Gemini (configurable in `core/config.py`) with agents orchestrating retrieval-first prompts to reduce tokens.
- Deployment: Container-ready; see Dockerfile below and run commands.
- Video (suggested): Short 2–3 minute screencast showing upload → status → ask/summary → MCP tool call. Script outline:
    1) Start server  2) Upload PDF  3) Show task status  4) Ask: “Summarize Chapter 3”  5) Call `pdf_search` via `/mcp/tools/*/call`  6) Close with OpenAPI tool schema.

PowerShell quick commands:
```
# Local run
python app.py

# After building container
docker build -t agentsangam:latest .
docker run -p 8000:8000 --env GOOGLE_API_KEY=$env:GOOGLE_API_KEY agentsangam:latest

# Hit endpoints
curl http://localhost:8000/mcp/tools
curl http://localhost:8000/openapi/tools/pdf_search
```
