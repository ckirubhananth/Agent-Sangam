"""
Model Context Protocol (MCP) Server for Agent Sangam PDF Tools

Implements the Model Context Protocol to expose PDF tools as standard MCP resources,
enabling external tools and agents to discover and use the PDF manipulation capabilities.

Reference: https://modelcontextprotocol.io/
"""

import json
import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPTool:
    """Represents a tool in MCP format."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", [])
            }
        }


class MCPResource:
    """Represents a resource in MCP format."""
    
    def __init__(self, uri: str, name: str, description: str, mimeType: str = "text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mimeType = mimeType
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource format."""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mimeType
        }


class AgentSangamMCPServer:
    """
    MCP Server for Agent Sangam PDF Tools.
    
    Exposes PDF manipulation tools through the Model Context Protocol,
    allowing other tools and agents to:
    - Discover available PDF tools
    - Call PDF tools with proper parameters
    - Get results in standardized format
    """
    
    def __init__(self, name: str = "Agent Sangam PDF Tools", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._initialize_tools()
        logger.info(f"[MCP Server] Initialized: {self.name} v{self.version}")
    
    def _initialize_tools(self) -> None:
        """Initialize all available PDF tools in MCP format."""
        
        # PDF Search Tool
        self.register_tool(
            MCPTool(
                name="pdf_search",
                description="Search indexed PDF content for passages matching a query",
                parameters={
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
            )
        )
        
        # Extract Entities Tool
        self.register_tool(
            MCPTool(
                name="extract_entities",
                description="Extract named entities from PDF (persons, dates, numbers, locations)",
                parameters={
                    "properties": {
                        "pdf_session_id": {
                            "type": "string",
                            "description": "ID of the PDF to extract from"
                        }
                    },
                    "required": ["pdf_session_id"]
                }
            )
        )
        
        # PDF Summary Tool
        self.register_tool(
            MCPTool(
                name="pdf_summary",
                description="Get overview of PDF document including key sections and entities",
                parameters={
                    "properties": {
                        "pdf_session_id": {
                            "type": "string",
                            "description": "ID of the PDF to summarize"
                        }
                    },
                    "required": ["pdf_session_id"]
                }
            )
        )
        
        # Context Retrieval Tool
        self.register_tool(
            MCPTool(
                name="retrieve_context",
                description="Retrieve relevant sections of PDF based on a question",
                parameters={
                    "properties": {
                        "pdf_session_id": {
                            "type": "string",
                            "description": "ID of the PDF to retrieve from"
                        },
                        "question": {
                            "type": "string",
                            "description": "Question to find relevant context for"
                        }
                    },
                    "required": ["pdf_session_id", "question"]
                }
            )
        )
        
        logger.info(f"[MCP Server] Registered {len(self.tools)} tools")
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool in the MCP server."""
        self.tools[tool.name] = tool
        logger.debug(f"[MCP Tools] Registered: {tool.name}")
    
    def register_resource(self, resource: MCPResource) -> None:
        """Register a resource in the MCP server."""
        self.resources[resource.uri] = resource
        logger.debug(f"[MCP Resources] Registered: {resource.uri}")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools in MCP format."""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        return self.tools.get(name)
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get all available resources in MCP format."""
        return [resource.to_dict() for resource in self.resources.values()]
    
    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """Get a specific resource by URI."""
        return self.resources.get(uri)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information in MCP format."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Model Context Protocol server for PDF document analysis tools",
            "capabilities": {
                "tools": {
                    "listChanged": False
                },
                "resources": {
                    "listChanged": False
                }
            },
            "toolCount": len(self.tools),
            "resourceCount": len(self.resources)
        }
    
    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI schema for all MCP tools."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.name,
                "version": self.version,
                "description": "PDF document analysis tools via Model Context Protocol"
            },
            "paths": {
                "/tools": {
                    "get": {
                        "summary": "List available tools",
                        "responses": {
                            "200": {
                                "description": "List of available tools",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "tools": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "name": {"type": "string"},
                                                            "description": {"type": "string"},
                                                            "inputSchema": {"type": "object"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/tools/{toolName}": {
                    "post": {
                        "summary": "Call a tool",
                        "parameters": [
                            {
                                "name": "toolName",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Tool execution result",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }


# Global MCP Server instance
_mcp_server: Optional[AgentSangamMCPServer] = None


def get_mcp_server() -> AgentSangamMCPServer:
    """Get or create the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = AgentSangamMCPServer()
    return _mcp_server


def initialize_mcp_server() -> AgentSangamMCPServer:
    """Initialize the MCP server."""
    return get_mcp_server()
