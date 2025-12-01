"""
Tests for OpenAPI Schema Generator

Validates:
- OpenAPI schema generation
- Tool definitions
- Schema compliance with OpenAPI 3.0
- Agent tool definitions format
"""

import pytest
import json
import logging
from core.openapi_generator import (
    OpenAPISchemaGenerator,
    get_openapi_generator,
    initialize_openapi_generator
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TestOpenAPISchemaGenerator:
    """Test OpenAPI schema generation."""
    
    def test_generator_initialization(self):
        """Test initializing OpenAPI generator."""
        generator = OpenAPISchemaGenerator()
        
        assert generator.title == "Agent Sangam API"
        assert generator.version == "1.0.0"
        assert len(generator.tools) == 4
        logger.info(f"[Test] Generator initialized with {len(generator.tools)} tools")
    
    def test_all_tools_registered(self):
        """Test all 4 tools are registered."""
        generator = OpenAPISchemaGenerator()
        
        expected_tools = ["pdf_search", "extract_entities", "pdf_summary", "retrieve_context"]
        registered_tools = list(generator.tools.keys())
        
        logger.info(f"[Test] Registered tools: {registered_tools}")
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools, f"Tool '{tool_name}' not registered"
            assert generator.get_tool_schema(tool_name) is not None
    
    def test_tool_schema_structure(self):
        """Test each tool has proper schema structure."""
        generator = OpenAPISchemaGenerator()
        
        for tool_name, tool_schema in generator.tools.items():
            assert "name" in tool_schema
            assert "summary" in tool_schema
            assert "description" in tool_schema
            assert "operationId" in tool_schema
            assert "parameters" in tool_schema
            assert "responses" in tool_schema
            assert "tags" in tool_schema
            logger.info(f"[Test] Tool '{tool_name}' has proper structure")
    
    def test_pdf_search_schema(self):
        """Test pdf_search tool schema."""
        generator = OpenAPISchemaGenerator()
        schema = generator.get_tool_schema("pdf_search")
        
        assert schema["name"] == "pdf_search"
        assert "search" in schema["summary"].lower()
        
        # Check parameters
        param_names = [p["name"] for p in schema["parameters"]]
        assert "pdf_session_id" in param_names
        assert "query" in param_names
        assert "max_results" in param_names
        
        # Check required params
        required_params = [p["name"] for p in schema["parameters"] if p["required"]]
        assert "pdf_session_id" in required_params
        assert "query" in required_params
        assert "max_results" not in required_params
        
        logger.info("[Test] pdf_search schema is correct")
    
    def test_extract_entities_schema(self):
        """Test extract_entities tool schema."""
        generator = OpenAPISchemaGenerator()
        schema = generator.get_tool_schema("extract_entities")
        
        assert schema["name"] == "extract_entities"
        assert "entit" in schema["summary"].lower()
        
        param_names = [p["name"] for p in schema["parameters"]]
        assert "pdf_session_id" in param_names
        assert len(schema["parameters"]) == 1
        
        logger.info("[Test] extract_entities schema is correct")
    
    def test_pdf_summary_schema(self):
        """Test pdf_summary tool schema."""
        generator = OpenAPISchemaGenerator()
        schema = generator.get_tool_schema("pdf_summary")
        
        assert schema["name"] == "pdf_summary"
        assert "summary" in schema["summary"].lower()
        
        param_names = [p["name"] for p in schema["parameters"]]
        assert "pdf_session_id" in param_names
        
        logger.info("[Test] pdf_summary schema is correct")
    
    def test_retrieve_context_schema(self):
        """Test retrieve_context tool schema."""
        generator = OpenAPISchemaGenerator()
        schema = generator.get_tool_schema("retrieve_context")
        
        assert schema["name"] == "retrieve_context"
        assert "context" in schema["summary"].lower()
        
        param_names = [p["name"] for p in schema["parameters"]]
        assert "pdf_session_id" in param_names
        assert "question" in param_names
        
        required_params = [p["name"] for p in schema["parameters"] if p["required"]]
        assert "question" in required_params
        
        logger.info("[Test] retrieve_context schema is correct")
    
    def test_openapi_spec_generation(self):
        """Test generating complete OpenAPI specification."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        # Check spec structure
        assert spec["openapi"] == "3.0.0"
        assert "info" in spec
        assert "servers" in spec
        assert "paths" in spec
        assert "components" in spec
        
        # Check info
        assert spec["info"]["title"] == "Agent Sangam API"
        assert spec["info"]["version"] == "1.0.0"
        
        # Check paths
        assert "/pdf/pdf_search" in spec["paths"]
        assert "/pdf/extract_entities" in spec["paths"]
        assert "/pdf/pdf_summary" in spec["paths"]
        assert "/pdf/retrieve_context" in spec["paths"]
        
        logger.info("[Test] OpenAPI spec generated correctly")
    
    def test_openapi_spec_servers(self):
        """Test OpenAPI spec has proper servers configured."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        assert len(spec["servers"]) >= 2
        server_urls = [s["url"] for s in spec["servers"]]
        assert "http://localhost:8000" in server_urls
        
        logger.info("[Test] OpenAPI spec has proper servers")
    
    def test_openapi_spec_components(self):
        """Test OpenAPI spec has proper components/schemas."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        schemas = spec["components"]["schemas"]
        assert "PDFSession" in schemas
        assert "SearchResult" in schemas
        assert "EntityExtraction" in schemas
        assert "Error" in schemas
        
        logger.info("[Test] OpenAPI spec has proper schemas")
    
    def test_openapi_spec_is_valid_json(self):
        """Test OpenAPI spec is valid JSON."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        # Should be serializable to JSON
        json_str = json.dumps(spec)
        assert isinstance(json_str, str)
        assert len(json_str) > 0
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["openapi"] == "3.0.0"
        
        logger.info("[Test] OpenAPI spec is valid JSON")


class TestToolDefinitions:
    """Test agent-ready tool definitions."""
    
    def test_get_tool_definition(self):
        """Test getting a tool definition for agents."""
        generator = OpenAPISchemaGenerator()
        definition = generator.get_tool_definition("pdf_search")
        
        assert definition["type"] == "function"
        assert "function" in definition
        assert definition["function"]["name"] == "pdf_search"
        assert "description" in definition["function"]
        assert "parameters" in definition["function"]
        
        logger.info("[Test] Tool definition has proper format")
    
    def test_tool_definition_parameters(self):
        """Test tool definition has proper parameter structure."""
        generator = OpenAPISchemaGenerator()
        definition = generator.get_tool_definition("pdf_search")
        
        params = definition["function"]["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params
        
        # Check pdf_search parameters
        props = params["properties"]
        assert "pdf_session_id" in props
        assert "query" in props
        assert "max_results" in props
        
        # Check required fields
        assert "pdf_session_id" in params["required"]
        assert "query" in params["required"]
        assert "max_results" not in params["required"]
        
        logger.info("[Test] Tool definition parameters are correct")
    
    def test_all_tool_definitions(self):
        """Test getting all tool definitions."""
        generator = OpenAPISchemaGenerator()
        definitions = generator.get_all_tool_definitions()
        
        assert len(definitions) == 4
        
        # Each should be a proper function definition
        for definition in definitions:
            assert definition["type"] == "function"
            assert "function" in definition
            assert "name" in definition["function"]
            assert "description" in definition["function"]
            assert "parameters" in definition["function"]
        
        tool_names = [d["function"]["name"] for d in definitions]
        assert "pdf_search" in tool_names
        assert "extract_entities" in tool_names
        assert "pdf_summary" in tool_names
        assert "retrieve_context" in tool_names
        
        logger.info(f"[Test] All {len(definitions)} tool definitions generated")
    
    def test_tool_definitions_for_agent_use(self):
        """Test tool definitions match agent/LLM requirements."""
        generator = OpenAPISchemaGenerator()
        definitions = generator.get_all_tool_definitions()
        
        # Test that these could be used by Claude/GPT
        for definition in definitions:
            # Each tool should have name and description
            assert len(definition["function"]["name"]) > 0
            assert len(definition["function"]["description"]) > 10
            
            # Parameters should be well-formed
            params = definition["function"]["parameters"]
            for prop_name, prop_schema in params.get("properties", {}).items():
                assert "type" in prop_schema
        
        logger.info("[Test] Tool definitions ready for agent use")


class TestOpenAPISingleton:
    """Test OpenAPI generator singleton pattern."""
    
    def test_get_openapi_generator(self):
        """Test getting OpenAPI generator instance."""
        gen1 = get_openapi_generator()
        gen2 = get_openapi_generator()
        
        # Should return same instance
        assert gen1 is gen2
        logger.info("[Test] Singleton pattern works correctly")
    
    def test_initialize_openapi_generator(self):
        """Test initializing OpenAPI generator."""
        gen = initialize_openapi_generator()
        
        assert isinstance(gen, OpenAPISchemaGenerator)
        assert len(gen.tools) == 4
        logger.info("[Test] OpenAPI generator initialized")


class TestOpenAPICompliance:
    """Test compliance with OpenAPI 3.0 specification."""
    
    def test_openapi_version_format(self):
        """Test OpenAPI version format."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        # OpenAPI version should be 3.0.0, 3.0.1, 3.1.0, etc.
        version = spec["openapi"]
        parts = version.split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts)
        logger.info(f"[Test] OpenAPI version {version} is valid")
    
    def test_required_info_fields(self):
        """Test OpenAPI info object has required fields."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        info = spec["info"]
        assert "title" in info
        assert "version" in info
        assert len(info["title"]) > 0
        assert len(info["version"]) > 0
        logger.info("[Test] Info object has required fields")
    
    def test_paths_format(self):
        """Test paths follow OpenAPI format."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        paths = spec["paths"]
        assert isinstance(paths, dict)
        
        for path, methods in paths.items():
            assert path.startswith("/")
            assert isinstance(methods, dict)
            # Should have HTTP methods (get, post, put, delete, etc.)
            valid_methods = ["get", "post", "put", "delete", "patch", "options", "head", "trace"]
            assert any(m in methods for m in valid_methods)
        
        logger.info("[Test] Paths follow OpenAPI format")
    
    def test_response_format(self):
        """Test responses follow OpenAPI format."""
        generator = OpenAPISchemaGenerator()
        spec = generator.generate_openapi_spec()
        
        for path, methods in spec["paths"].items():
            for method, operation in methods.items():
                if "responses" in operation:
                    responses = operation["responses"]
                    assert isinstance(responses, dict)
                    # Should have at least one response code
                    assert any(code.isdigit() or code == "default" for code in responses.keys())
        
        logger.info("[Test] Responses follow OpenAPI format")


class TestOpenAPIExport:
    """Test exporting OpenAPI spec to file."""
    
    def test_export_openapi_json(self, tmp_path):
        """Test exporting OpenAPI spec to JSON file."""
        generator = OpenAPISchemaGenerator()
        
        # Export to temporary file
        output_file = tmp_path / "openapi.json"
        generator.export_openapi_json(str(output_file))
        
        # Verify file exists and contains valid JSON
        assert output_file.exists()
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert data["openapi"] == "3.0.0"
        assert len(data["paths"]) == 4
        
        logger.info(f"[Test] OpenAPI spec exported to {output_file}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
