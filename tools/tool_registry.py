"""
Tool Registry and Discovery System

Provides centralized tool management and discovery for agents.
Enables dynamic tool lookup, metadata retrieval, and OpenAPI schema generation.
"""

import logging
from typing import Dict, List, Optional
from google.genai import types

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all agent tools."""
    
    def __init__(self):
        self._tools: Dict[str, 'BaseTool'] = {}
        self._tool_metadata: Dict[str, dict] = {}
        
    def register(self, tool) -> None:
        """Register a tool in the registry."""
        tool_name = tool.name
        self._tools[tool_name] = tool
        
        # Extract metadata from tool's FunctionDeclaration
        declaration = tool._get_declaration()
        self._tool_metadata[tool_name] = {
            "name": declaration.name,
            "description": declaration.description,
            "parameters": declaration.parameters_json_schema,
        }
        
        logger.info(f"[ToolRegistry] Registered tool: {tool_name}")
    
    def get_tool(self, tool_name: str):
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_all_tool_names(self) -> List[str]:
        """Get all registered tool names."""
        return list(self._tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[dict]:
        """Get metadata for a specific tool."""
        return self._tool_metadata.get(tool_name)
    
    def get_all_metadata(self) -> Dict[str, dict]:
        """Get metadata for all tools."""
        return self._tool_metadata.copy()
    
    def generate_openapi_schema(self) -> dict:
        """Generate OpenAPI schema for all registered tools."""
        tools_schema = {}
        for tool_name, metadata in self._tool_metadata.items():
            tools_schema[tool_name] = {
                "description": metadata["description"],
                "parameters": metadata["parameters"],
            }
        
        return {
            "tools": tools_schema,
            "total": len(tools_schema),
            "registry_version": "1.0",
        }
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ToolRegistry(tools={len(self._tools)}, names={self.get_all_tool_names()})"


# Global tool registry instance
_global_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry


def register_tool(tool) -> None:
    """Register a tool in the global registry."""
    _global_registry.register(tool)


def get_all_tools() -> List:
    """Get all registered tools."""
    return _global_registry.get_all_tools()


def get_tool(tool_name: str):
    """Get a tool by name from the global registry."""
    return _global_registry.get_tool(tool_name)


def generate_tools_schema() -> dict:
    """Generate OpenAPI schema for all tools."""
    return _global_registry.generate_openapi_schema()


# Initialize registry with all tools on import
def _initialize_registry():
    """Initialize the registry with all tools."""
    try:
        from tools.agent_tools import ALL_TOOLS
        for tool in ALL_TOOLS:
            register_tool(tool)
        logger.info(f"[ToolRegistry] Initialized with {len(_global_registry)} tools")
    except ImportError as e:
        logger.warning(f"[ToolRegistry] Could not initialize tools: {e}")


# Auto-initialize on import
_initialize_registry()
