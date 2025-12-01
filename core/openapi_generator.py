"""
OpenAPI Schema Generator for Agent Sangam Tools

Generates formal OpenAPI 3.0 specifications for all PDF tools,
enabling automatic documentation, client generation, and tool discovery.
"""

import json
import os
from typing import Any, Dict, List, Optional
from tools.agent_tools import (
    PDFSearchTool, PDFEntityExtractorTool, 
    PDFSummaryTool, PDFContextRetrievalTool
)


class OpenAPISchemaGenerator:
    """Generate OpenAPI 3.0 schemas for PDF tools."""
    
    def __init__(self, title: str = "Agent Sangam API", version: str = "1.0.0"):
        self.title = title
        self.version = version
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """Initialize tool definitions with OpenAPI schemas."""
        
        # Tool 1: PDF Search
        self.tools["pdf_search"] = {
            "name": "pdf_search",
            "summary": "Search PDF Content",
            "description": "Search indexed PDF content for passages matching a query. Returns relevant text excerpts.",
            "operationId": "searchPDF",
            "tags": ["PDF Operations"],
            "parameters": [
                {
                    "name": "pdf_session_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Unique identifier for the PDF session"
                },
                {
                    "name": "query",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Search query to find in PDF"
                },
                {
                    "name": "max_results",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "default": 5, "minimum": 1, "maximum": 50},
                    "description": "Maximum number of results to return"
                }
            ],
            "responses": {
                "200": {
                    "description": "Search results found",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "results": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of matching passages"
                                    },
                                    "count": {
                                        "type": "integer",
                                        "description": "Number of results"
                                    },
                                    "query": {
                                        "type": "string",
                                        "description": "The search query used"
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {"description": "Missing required parameters"},
                "404": {"description": "PDF session not found"}
            }
        }
        
        # Tool 2: Extract Entities
        self.tools["extract_entities"] = {
            "name": "extract_entities",
            "summary": "Extract Entities from PDF",
            "description": "Extract named entities (persons, dates, numbers, locations) from PDF document.",
            "operationId": "extractEntities",
            "tags": ["PDF Operations"],
            "parameters": [
                {
                    "name": "pdf_session_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Unique identifier for the PDF session"
                }
            ],
            "responses": {
                "200": {
                    "description": "Entities extracted successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "persons": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Names of people mentioned"
                                    },
                                    "dates": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Dates found in document"
                                    },
                                    "numbers": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Significant numbers"
                                    },
                                    "locations": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Geographic locations mentioned"
                                    }
                                }
                            }
                        }
                    }
                },
                "404": {"description": "PDF session not found"}
            }
        }
        
        # Tool 3: PDF Summary
        self.tools["pdf_summary"] = {
            "name": "pdf_summary",
            "summary": "Get PDF Summary",
            "description": "Get a comprehensive overview of PDF document including key sections, entities, and main topics.",
            "operationId": "summarizePDF",
            "tags": ["PDF Operations"],
            "parameters": [
                {
                    "name": "pdf_session_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Unique identifier for the PDF session"
                }
            ],
            "responses": {
                "200": {
                    "description": "Summary generated successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "overview": {
                                        "type": "string",
                                        "description": "High-level document overview"
                                    },
                                    "key_topics": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Main topics covered"
                                    },
                                    "key_entities": {
                                        "type": "object",
                                        "description": "Important entities extracted"
                                    }
                                }
                            }
                        }
                    }
                },
                "404": {"description": "PDF session not found"}
            }
        }
        
        # Tool 4: Retrieve Context
        self.tools["retrieve_context"] = {
            "name": "retrieve_context",
            "summary": "Retrieve Relevant Context",
            "description": "Retrieve relevant sections of PDF based on a question or query.",
            "operationId": "retrieveContext",
            "tags": ["PDF Operations"],
            "parameters": [
                {
                    "name": "pdf_session_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Unique identifier for the PDF session"
                },
                {
                    "name": "question",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Question to find relevant context for"
                }
            ],
            "responses": {
                "200": {
                    "description": "Relevant context retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "context": {
                                        "type": "string",
                                        "description": "Relevant document excerpts"
                                    },
                                    "relevance": {
                                        "type": "number",
                                        "description": "Relevance score (0-1)"
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {"description": "Missing required parameters"},
                "404": {"description": "PDF session not found"}
            }
        }
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get OpenAPI schema for a specific tool."""
        return self.tools.get(tool_name)
    
    def get_all_tools_schemas(self) -> Dict[str, Any]:
        """Get OpenAPI schemas for all tools."""
        return self.tools
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification."""
        
        paths = {}
        
        # Create OpenAPI paths for each tool
        for tool_name, tool_schema in self.tools.items():
            path_key = f"/pdf/{tool_name}"
            
            paths[path_key] = {
                "get": {
                    "summary": tool_schema["summary"],
                    "description": tool_schema["description"],
                    "operationId": tool_schema["operationId"],
                    "tags": tool_schema["tags"],
                    "parameters": tool_schema["parameters"],
                    "responses": tool_schema["responses"]
                }
            }
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "description": "API for PDF document analysis and tool operations",
                "version": self.version,
                "contact": {
                    "name": "Agent Sangam Support"
                }
            },
            "servers": [
                {
                    "url": f"http://localhost:{os.getenv('PORT', '8000')}",
                    "description": "Local development server"
                },
                {
                    "url": "https://api.agentsangam.example.com",
                    "description": "Production server"
                }
            ],
            "tags": [
                {
                    "name": "PDF Operations",
                    "description": "Operations for PDF document analysis"
                }
            ],
            "paths": paths,
            "components": {
                "schemas": {
                    "PDFSession": {
                        "type": "object",
                        "properties": {
                            "pdf_session_id": {
                                "type": "string",
                                "description": "Unique PDF session identifier"
                            },
                            "pdf_name": {
                                "type": "string",
                                "description": "Original PDF filename"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["uploaded", "ingested", "indexed", "ready"],
                                "description": "Current processing status"
                            }
                        },
                        "required": ["pdf_session_id", "pdf_name", "status"]
                    },
                    "SearchResult": {
                        "type": "object",
                        "properties": {
                            "results": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "count": {"type": "integer"},
                            "query": {"type": "string"}
                        }
                    },
                    "EntityExtraction": {
                        "type": "object",
                        "properties": {
                            "persons": {"type": "array", "items": {"type": "string"}},
                            "dates": {"type": "array", "items": {"type": "string"}},
                            "numbers": {"type": "array", "items": {"type": "string"}},
                            "locations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "message": {"type": "string"},
                            "status_code": {"type": "integer"}
                        }
                    }
                }
            }
        }
    
    def export_openapi_json(self, filepath: str) -> None:
        """Export OpenAPI spec to JSON file."""
        spec = self.generate_openapi_spec()
        with open(filepath, 'w') as f:
            json.dump(spec, f, indent=2)
    
    def get_tool_definition(self, tool_name: str) -> Dict[str, Any]:
        """Get formal definition of a tool for agent use."""
        tool = self.tools.get(tool_name)
        if not tool:
            return {}
        
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        param["name"]: {
                            "type": param["schema"].get("type", "string"),
                            "description": param.get("description", "")
                        }
                        for param in tool["parameters"]
                    },
                    "required": [
                        param["name"] for param in tool["parameters"] 
                        if param.get("required")
                    ]
                }
            }
        }
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get formal definitions of all tools for agents."""
        return [
            self.get_tool_definition(tool_name)
            for tool_name in self.tools.keys()
        ]


# Global OpenAPI generator instance
_openapi_generator: Optional[OpenAPISchemaGenerator] = None


def get_openapi_generator() -> OpenAPISchemaGenerator:
    """Get or create the global OpenAPI generator instance."""
    global _openapi_generator
    if _openapi_generator is None:
        _openapi_generator = OpenAPISchemaGenerator()
    return _openapi_generator


def initialize_openapi_generator() -> OpenAPISchemaGenerator:
    """Initialize the OpenAPI generator."""
    return get_openapi_generator()
