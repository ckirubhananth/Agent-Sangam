# Model Context Protocol (MCP) Server Implementation

## Overview

The Agent Sangam project now includes a complete **Model Context Protocol (MCP) server** that exposes all PDF tools through the standardized MCP interface. This enables seamless integration with external AI tools, agents, and applications that support the Model Context Protocol.

**MCP Specification:** https://modelcontextprotocol.io/

## What is the Model Context Protocol?

The Model Context Protocol is an open standard developed by Anthropic for building AI agents and tools. It provides:

- **Standard Tool Definitions**: Consistent format for describing tools and their capabilities
- **Tool Discovery**: Clients can discover available tools and their schemas
- **Type Safety**: Input/output validation through JSON schema
- **Interoperability**: Tools work with any MCP-compatible client or agent

## MCP Architecture in Agent Sangam

### Components

```
┌─────────────────────────────────────────┐
│     FastAPI Application (app.py)        │
├─────────────────────────────────────────┤
│  MCP Routes (/mcp/*)                    │
│  ├─ GET /mcp/info                       │
│  ├─ GET /mcp/tools                      │
│  ├─ GET /mcp/tools/{name}               │
│  ├─ POST /mcp/tools/{name}/call         │
│  ├─ GET /mcp/resources                  │
│  └─ GET /mcp/schema                     │
├─────────────────────────────────────────┤
│  MCP Server (core/mcp_server.py)        │
│  ├─ AgentSangamMCPServer class          │
│  ├─ MCPTool (tool representation)       │
│  └─ MCPResource (resource representation)
├─────────────────────────────────────────┤
│  PDF Tools Integration                  │
│  ├─ pdf_search                          │
│  ├─ extract_entities                    │
│  ├─ pdf_summary                         │
│  └─ retrieve_context                    │
└─────────────────────────────────────────┘
```

### Files

**New MCP Files:**
- `core/mcp_server.py` - MCP server implementation (350+ lines)
- `tests/test_mcp_server.py` - Comprehensive test suite (400+ lines)

**Modified Files:**
- `routes.py` - Added 6 new MCP endpoints (100+ lines)

## Exposed MCP Tools

The MCP server exposes 4 PDF tools in standardized MCP format:

### 1. PDF Search Tool
```
Name: pdf_search
Description: Search indexed PDF content for passages matching a query
Parameters:
  - pdf_session_id (required): ID of the PDF to search
  - query (required): Search query
  - max_results (optional): Maximum number of results (default: 5)
```

### 2. Extract Entities Tool
```
Name: extract_entities
Description: Extract named entities from PDF (persons, dates, numbers, locations)
Parameters:
  - pdf_session_id (required): ID of the PDF to extract from
```

### 3. PDF Summary Tool
```
Name: pdf_summary
Description: Get overview of PDF document including key sections and entities
Parameters:
  - pdf_session_id (required): ID of the PDF to summarize
```

### 4. Retrieve Context Tool
```
Name: retrieve_context
Description: Retrieve relevant sections of PDF based on a question
Parameters:
  - pdf_session_id (required): ID of the PDF to retrieve from
  - question (required): Question to find relevant context for
```

## MCP Endpoints

### 1. Get Server Information
```
GET /mcp/info
```

**Response:**
```json
{
  "name": "Agent Sangam PDF Tools",
  "version": "1.0.0",
  "description": "Model Context Protocol server for PDF document analysis tools",
  "capabilities": {
    "tools": {
      "listChanged": false
    },
    "resources": {
      "listChanged": false
    }
  },
  "toolCount": 4,
  "resourceCount": 0
}
```

### 2. List Available Tools
```
GET /mcp/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "pdf_search",
      "description": "Search indexed PDF content for passages matching a query",
      "inputSchema": {
        "type": "object",
        "properties": {
          "pdf_session_id": {
            "type": "string",
            "description": "ID of the PDF to search"
          },
          "query": {
            "type": "string",
            "description": "Search query"
          },
          "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "default": 5
          }
        },
        "required": ["pdf_session_id", "query"]
      }
    },
    // ... more tools
  ],
  "totalTools": 4
}
```

### 3. Get Specific Tool Definition
```
GET /mcp/tools/{tool_name}
```

**Example:**
```
GET /mcp/tools/pdf_search
```

**Response:**
```json
{
  "name": "pdf_search",
  "description": "Search indexed PDF content for passages matching a query",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pdf_session_id": {
        "type": "string",
        "description": "ID of the PDF to search"
      },
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results to return",
        "default": 5
      }
    },
    "required": ["pdf_session_id", "query"]
  }
}
```

### 4. Call a Tool
```
POST /mcp/tools/{tool_name}/call
Content-Type: application/json

{
  "pdf_session_id": "session-id",
  "query": "search term"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/tools/pdf_search/call \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_session_id": "myPDF_123",
    "query": "quantum physics",
    "max_results": 10
  }'
```

**Response:**
```json
{
  "tool": "pdf_search",
  "status": "success",
  "result": "Search results from PDF..."
}
```

### 5. List Resources
```
GET /mcp/resources
```

**Response:**
```json
{
  "resources": [],
  "totalResources": 0
}
```

### 6. Get OpenAPI Schema
```
GET /mcp/schema
```

**Response:**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Agent Sangam PDF Tools",
    "version": "1.0.0",
    "description": "PDF document analysis tools via Model Context Protocol"
  },
  "paths": {
    "/tools": { /* ... */ },
    "/tools/{toolName}": { /* ... */ }
  }
}
```

## Integration Examples

### Using with Claude (via MCP)

If Claude supports Agent Sangam as an MCP server:

```python
# In Claude's MCP configuration
{
  "mcpServers": {
    "agent-sangam": {
      "command": "python",
      "args": ["path/to/start_server.py"],
      "url": "http://localhost:8000"
    }
  }
}

# Then Claude can use:
tools.use("pdf_search", {
  "pdf_session_id": "myPDF",
  "query": "important concept"
})
```

### Using with Custom Agents

```python
import requests
import json

# Discover tools
response = requests.get("http://localhost:8000/mcp/tools")
tools = response.json()["tools"]

# Call a tool
result = requests.post(
    "http://localhost:8000/mcp/tools/pdf_search/call",
    json={
        "pdf_session_id": "myPDF",
        "query": "search term"
    }
)

answer = result.json()["result"]
```

### Using with LangChain

```python
from langchain.tools import Tool
import requests

def call_mcp_tool(tool_name: str, **kwargs):
    response = requests.post(
        f"http://localhost:8000/mcp/tools/{tool_name}/call",
        json=kwargs
    )
    return response.json()["result"]

# Create LangChain tools from MCP definitions
pdf_search_tool = Tool(
    name="pdf_search",
    func=lambda query, pdf_session_id: call_mcp_tool(
        "pdf_search",
        query=query,
        pdf_session_id=pdf_session_id
    ),
    description="Search PDF content"
)
```

## Code Structure

### MCPTool Class
Represents a single tool in MCP format:

```python
class MCPTool:
    def __init__(self, name: str, description: str, parameters: Dict):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", [])
            }
        }
```

### MCPResource Class
Represents a resource (e.g., uploaded PDF):

```python
class MCPResource:
    def __init__(self, uri: str, name: str, description: str, mimeType: str):
        self.uri = uri
        self.name = name
        self.description = description
        self.mimeType = mimeType
```

### AgentSangamMCPServer Class
Main MCP server implementation:

```python
class AgentSangamMCPServer:
    def __init__(self, name: str = "Agent Sangam PDF Tools", version: str = "1.0.0"):
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._initialize_tools()
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in MCP format"""
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server capabilities"""
    
    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI schema"""
```

## Testing

Run MCP tests:

```bash
# Test MCP server implementation
pytest tests/test_mcp_server.py -v

# Test specific test class
pytest tests/test_mcp_server.py::TestAgentSangamMCPServer -v

# Run with detailed logging
pytest tests/test_mcp_server.py -v -s
```

### Test Coverage

The test suite includes:

- **MCPTool tests**: Tool creation and serialization
- **MCPResource tests**: Resource creation and serialization
- **Server initialization tests**: Proper setup of 4 PDF tools
- **Tool registration tests**: Adding custom tools dynamically
- **Format validation tests**: JSON schema compliance
- **Singleton pattern tests**: Server instance management
- **Tool definition tests**: Correct parameters and schemas

Example test output:
```
tests/test_mcp_server.py::TestMCPTool::test_tool_creation PASSED
tests/test_mcp_server.py::TestAgentSangamMCPServer::test_server_initialization PASSED
tests/test_mcp_server.py::TestAgentSangamMCPServer::test_tools_registered PASSED
tests/test_mcp_server.py::TestMCPToolFormats::test_all_tools_have_required_fields PASSED
...
```

## Deployment

### Docker Integration

The MCP server is integrated into the existing FastAPI app:

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# MCP endpoints available at /mcp/*
EXPOSE 8000

CMD ["python", "app.py"]
```

### Starting the Server

```bash
# Set API key
export GOOGLE_API_KEY="your-key"

# Run the server
python app.py

# MCP endpoints are now available:
# - http://localhost:8000/mcp/info
# - http://localhost:8000/mcp/tools
# - http://localhost:8000/mcp/tools/{name}
# etc.
```

## Security Considerations

### Current Implementation

- All MCP endpoints are currently **open** (no authentication)
- Tools execute in the same context as the main application
- PDF session IDs are user-provided

### Recommended Security Enhancements

```python
# Add authentication to MCP endpoints
from fastapi import Depends, HTTPException

async def verify_api_key(api_key: str = Header(None)):
    if not api_key or api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")

@router.get("/mcp/tools")
async def mcp_list_tools(verified: bool = Depends(verify_api_key)):
    # Only accessible with valid API key
    pass
```

```python
# Add input validation
from pydantic import BaseModel, validator

class MCPToolCall(BaseModel):
    pdf_session_id: str
    query: str = None
    
    @validator("pdf_session_id")
    def validate_session_id(cls, v):
        # Ensure session exists and user owns it
        if v not in global_pdfs:
            raise ValueError("Session not found")
        return v
```

## Future Enhancements

1. **Tool Versioning**: Support multiple versions of tools
2. **Tool Plugins**: Allow third-party tools to register with MCP server
3. **Resource Management**: Expose uploaded PDFs as MCP resources
4. **Caching**: Cache tool results to improve performance
5. **Streaming**: Support streaming responses for large results
6. **Monitoring**: Add metrics and monitoring for MCP tool usage
7. **Rate Limiting**: Implement rate limiting per client/tool
8. **Custom Tools**: Allow agents to create and register custom tools

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **Tool Integration Docs**: See `TOOL_INTEGRATION.md`
- **API Documentation**: See `/static/index.html` or visit `http://localhost:8000/docs`
- **Test Suite**: `tests/test_mcp_server.py`

## Troubleshooting

### MCP Endpoints Not Responding

1. Check server is running: `curl http://localhost:8000/mcp/info`
2. Verify routes are registered: Check `routes.py` imports
3. Check logs: `docker logs agent-sangam` or terminal output

### Tool Not Found

1. Verify tool name matches exactly: `pdf_search` not `pdfSearch`
2. List available tools: `GET /mcp/tools`
3. Check tool is initialized in `AgentSangamMCPServer._initialize_tools()`

### Tool Call Failing

1. Verify PDF session ID exists: `GET /sessions`
2. Check required parameters are provided
3. Review error message in response: `"result"` field in response
4. Check server logs for detailed error trace

## Summary

The MCP server implementation provides a standardized, interoperable interface for all PDF tools in Agent Sangam. External tools, agents, and applications can discover and use these tools through the Model Context Protocol, enabling seamless integration in the broader AI ecosystem.

**Status: ✅ IMPLEMENTED**

- 4 PDF tools exposed via MCP (pdf_search, extract_entities, pdf_summary, retrieve_context)
- 6 MCP endpoints for discovery and invocation
- OpenAPI schema generation for tool documentation
- Comprehensive test suite (450+ lines)
- Full documentation and integration examples
