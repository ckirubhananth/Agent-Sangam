"""
Tests for Model Context Protocol (MCP) Server implementation.

Validates that:
- MCP server initializes correctly
- Tools are properly registered in MCP format
- OpenAPI schema is generated correctly
- MCP endpoints are accessible
"""

import pytest
import json
import logging
from unittest.mock import MagicMock, patch, AsyncMock
from core.mcp_server import (
    MCPTool, MCPResource, AgentSangamMCPServer,
    get_mcp_server, initialize_mcp_server
)

logger = logging.getLogger(__name__)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestMCPTool:
    """Test MCPTool class."""
    
    def test_tool_creation(self):
        """Test creating an MCP tool."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            parameters={
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
    
    def test_tool_to_dict(self):
        """Test converting MCP tool to dictionary."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            parameters={
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        )
        
        tool_dict = tool.to_dict()
        
        assert tool_dict["name"] == "test_tool"
        assert tool_dict["description"] == "A test tool"
        assert "inputSchema" in tool_dict
        assert tool_dict["inputSchema"]["type"] == "object"
        assert "properties" in tool_dict["inputSchema"]
        assert tool_dict["inputSchema"]["required"] == ["param1"]


class TestMCPResource:
    """Test MCPResource class."""
    
    def test_resource_creation(self):
        """Test creating an MCP resource."""
        resource = MCPResource(
            uri="pdf://document1",
            name="Document 1",
            description="Test document",
            mimeType="application/pdf"
        )
        
        assert resource.uri == "pdf://document1"
        assert resource.name == "Document 1"
    
    def test_resource_to_dict(self):
        """Test converting MCP resource to dictionary."""
        resource = MCPResource(
            uri="pdf://document1",
            name="Document 1",
            description="Test document",
            mimeType="application/pdf"
        )
        
        resource_dict = resource.to_dict()
        
        assert resource_dict["uri"] == "pdf://document1"
        assert resource_dict["name"] == "Document 1"
        assert resource_dict["mimeType"] == "application/pdf"


class TestAgentSangamMCPServer:
    """Test AgentSangamMCPServer class."""
    
    def test_server_initialization(self):
        """Test MCP server initialization."""
        server = AgentSangamMCPServer()
        
        assert server.name == "Agent Sangam PDF Tools"
        assert server.version == "1.0.0"
        assert len(server.tools) == 4  # Should have 4 PDF tools
        logger.info(f"[Test] Server initialized with {len(server.tools)} tools")
    
    def test_tools_registered(self):
        """Test that all tools are properly registered."""
        server = AgentSangamMCPServer()
        
        expected_tools = ["pdf_search", "extract_entities", "pdf_summary", "retrieve_context"]
        registered_tools = list(server.tools.keys())
        
        logger.info(f"[Test] Registered tools: {registered_tools}")
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools, f"Tool '{tool_name}' not registered"
            tool = server.get_tool(tool_name)
            assert tool is not None
            assert tool.name == tool_name
    
    def test_get_tools_format(self):
        """Test that tools are returned in proper MCP format."""
        server = AgentSangamMCPServer()
        tools = server.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 4
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
            logger.info(f"[Test] Tool '{tool['name']}' has proper MCP format")
    
    def test_register_tool(self):
        """Test registering a new tool."""
        server = AgentSangamMCPServer()
        initial_count = len(server.tools)
        
        new_tool = MCPTool(
            name="custom_tool",
            description="A custom tool",
            parameters={
                "properties": {"input": {"type": "string"}},
                "required": ["input"]
            }
        )
        
        server.register_tool(new_tool)
        
        assert len(server.tools) == initial_count + 1
        assert server.get_tool("custom_tool") is not None
        logger.info(f"[Test] Successfully registered custom tool")
    
    def test_register_resource(self):
        """Test registering a resource."""
        server = AgentSangamMCPServer()
        
        resource = MCPResource(
            uri="pdf://test",
            name="Test PDF",
            description="Test document"
        )
        
        server.register_resource(resource)
        
        assert len(server.resources) == 1
        assert server.get_resource("pdf://test") is not None
        logger.info(f"[Test] Successfully registered resource")
    
    def test_server_info(self):
        """Test getting server information."""
        server = AgentSangamMCPServer()
        info = server.get_server_info()
        
        assert info["name"] == "Agent Sangam PDF Tools"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert info["toolCount"] == 4
        logger.info(f"[Test] Server info: {json.dumps(info, indent=2)}")
    
    def test_openapi_schema_generation(self):
        """Test OpenAPI schema generation."""
        server = AgentSangamMCPServer()
        schema = server.generate_openapi_schema()
        
        assert schema["openapi"] == "3.0.0"
        assert "info" in schema
        assert schema["info"]["title"] == "Agent Sangam PDF Tools"
        assert "paths" in schema
        assert "/tools" in schema["paths"]
        assert "/tools/{toolName}" in schema["paths"]
        logger.info(f"[Test] OpenAPI schema generated with {len(schema['paths'])} paths")
    
    def test_get_tool_by_name(self):
        """Test retrieving a specific tool by name."""
        server = AgentSangamMCPServer()
        
        tool = server.get_tool("pdf_search")
        assert tool is not None
        assert tool.name == "pdf_search"
        assert "search" in tool.description.lower()
        logger.info(f"[Test] Retrieved tool: {tool.name}")
    
    def test_get_nonexistent_tool(self):
        """Test retrieving a nonexistent tool."""
        server = AgentSangamMCPServer()
        
        tool = server.get_tool("nonexistent_tool")
        assert tool is None
        logger.info(f"[Test] Nonexistent tool returns None as expected")


class TestMCPServerSingleton:
    """Test MCP server singleton pattern."""
    
    def test_get_mcp_server(self):
        """Test getting MCP server instance."""
        server1 = get_mcp_server()
        server2 = get_mcp_server()
        
        # Should return the same instance
        assert server1 is server2
        logger.info(f"[Test] Singleton pattern works: same instance returned")
    
    def test_initialize_mcp_server(self):
        """Test initializing MCP server."""
        server = initialize_mcp_server()
        
        assert isinstance(server, AgentSangamMCPServer)
        assert len(server.tools) > 0
        logger.info(f"[Test] MCP server initialized successfully")


class TestMCPPDFTools:
    """Test MCP tool definitions for PDF operations."""
    
    def test_pdf_search_tool_definition(self):
        """Test pdf_search tool has correct definition."""
        server = AgentSangamMCPServer()
        tool = server.get_tool("pdf_search")
        
        assert tool.name == "pdf_search"
        schema = tool.parameters
        assert "pdf_session_id" in schema["required"]
        assert "query" in schema["required"]
        assert "max_results" in schema["properties"]
        logger.info(f"[Test] pdf_search tool definition is correct")
    
    def test_extract_entities_tool_definition(self):
        """Test extract_entities tool has correct definition."""
        server = AgentSangamMCPServer()
        tool = server.get_tool("extract_entities")
        
        assert tool.name == "extract_entities"
        schema = tool.parameters
        assert "pdf_session_id" in schema["required"]
        logger.info(f"[Test] extract_entities tool definition is correct")
    
    def test_pdf_summary_tool_definition(self):
        """Test pdf_summary tool has correct definition."""
        server = AgentSangamMCPServer()
        tool = server.get_tool("pdf_summary")
        
        assert tool.name == "pdf_summary"
        schema = tool.parameters
        assert "pdf_session_id" in schema["required"]
        logger.info(f"[Test] pdf_summary tool definition is correct")
    
    def test_retrieve_context_tool_definition(self):
        """Test retrieve_context tool has correct definition."""
        server = AgentSangamMCPServer()
        tool = server.get_tool("retrieve_context")
        
        assert tool.name == "retrieve_context"
        schema = tool.parameters
        assert "pdf_session_id" in schema["required"]
        assert "question" in schema["required"]
        logger.info(f"[Test] retrieve_context tool definition is correct")


class TestMCPToolFormats:
    """Test that MCP tools have proper format for external consumption."""
    
    def test_all_tools_have_required_fields(self):
        """Test all tools have required MCP fields."""
        server = AgentSangamMCPServer()
        tools = server.get_tools()
        
        for tool in tools:
            assert "name" in tool, f"Tool missing 'name'"
            assert "description" in tool, f"Tool '{tool.get('name')}' missing 'description'"
            assert "inputSchema" in tool, f"Tool '{tool.get('name')}' missing 'inputSchema'"
            assert isinstance(tool["inputSchema"], dict), f"Tool '{tool['name']}' inputSchema is not dict"
            logger.info(f"[Test] Tool '{tool['name']}' has all required fields")
    
    def test_input_schemas_are_json_serializable(self):
        """Test that input schemas are JSON serializable."""
        server = AgentSangamMCPServer()
        tools = server.get_tools()
        
        for tool in tools:
            try:
                json_str = json.dumps(tool["inputSchema"])
                assert isinstance(json_str, str)
                logger.info(f"[Test] Tool '{tool['name']}' schema is JSON serializable")
            except Exception as e:
                pytest.fail(f"Tool '{tool['name']}' schema is not JSON serializable: {e}")
    
    def test_tool_descriptions_are_meaningful(self):
        """Test that all tools have meaningful descriptions."""
        server = AgentSangamMCPServer()
        tools = server.get_tools()
        
        for tool in tools:
            desc = tool["description"]
            assert len(desc) > 10, f"Tool '{tool['name']}' description is too short"
            assert desc[0].isupper(), f"Tool '{tool['name']}' description doesn't start with uppercase"
            logger.info(f"[Test] Tool '{tool['name']}' has meaningful description")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
