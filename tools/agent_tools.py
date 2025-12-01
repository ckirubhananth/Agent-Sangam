"""
Agent-compatible tool wrappers for PDF operations.
These classes inherit from BaseTool for compatibility with google.adk.agents.LlmAgent.
"""
import logging
from typing import Optional
from google.adk.tools import BaseTool
from google.genai import types
from tools.pdf_tools import (
    index_pdf_content,
    search_pdf,
    extract_entities,
    get_pdf_summary,
    retrieve_relevant_context,
    pdf_content_index
)

logger = logging.getLogger(__name__)


class PDFSearchTool(BaseTool):
    """Tool for searching indexed PDF content."""
    
    def __init__(self):
        super().__init__(
            name="pdf_search",
            description="Search the indexed PDF document for relevant passages matching a query."
        )
    
    def _get_declaration(self) -> types.FunctionDeclaration:
        """Get the function declaration for the LLM."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema={
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
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["pdf_session_id", "query"]
            }
        )
    
    async def run_async(self, **kwargs) -> str:
        """Execute the tool asynchronously."""
        pdf_session_id = kwargs.get("pdf_session_id")
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        
        logger.info(f"[PDFSearchTool] Searching {pdf_session_id} for: {query}")
        results = search_pdf(pdf_session_id, query, max_results)
        
        if not results:
            return "No relevant passages found in the PDF for this query."
        
        output = f"Found {len(results)} relevant passages:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['text'][:200]}...\n"
        
        return output


class PDFEntityExtractorTool(BaseTool):
    """Tool for extracting entities from PDF."""
    
    def __init__(self):
        super().__init__(
            name="extract_entities",
            description="Extract named entities (persons, locations, dates, numbers) from the PDF document."
        )
    
    def _get_declaration(self) -> types.FunctionDeclaration:
        """Get the function declaration for the LLM."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "pdf_session_id": {
                        "type": "string",
                        "description": "ID of the PDF to extract entities from"
                    }
                },
                "required": ["pdf_session_id"]
            }
        )
    
    async def run_async(self, **kwargs) -> str:
        """Execute the tool asynchronously."""
        pdf_session_id = kwargs.get("pdf_session_id")
        
        logger.info(f"[PDFEntityExtractorTool] Extracting entities from {pdf_session_id}")
        
        if pdf_session_id not in pdf_content_index:
            return "PDF not indexed. Please upload a PDF first."
        
        entities = pdf_content_index[pdf_session_id].get("entities", [])
        
        if not entities:
            return "No entities found in the PDF."
        
        output = "Key entities found in the PDF:\n\n"
        for entity in entities[:10]:
            output += f"- {entity['text']} ({entity['type']}) - mentioned {entity['count']} times\n"
        
        return output


class PDFSummaryTool(BaseTool):
    """Tool for getting PDF overview."""
    
    def __init__(self):
        super().__init__(
            name="pdf_summary",
            description="Get a summary/overview of the PDF document including key sections and entities."
        )
    
    def _get_declaration(self) -> types.FunctionDeclaration:
        """Get the function declaration for the LLM."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "pdf_session_id": {
                        "type": "string",
                        "description": "ID of the PDF to summarize"
                    }
                },
                "required": ["pdf_session_id"]
            }
        )
    
    async def run_async(self, **kwargs) -> str:
        """Execute the tool asynchronously."""
        pdf_session_id = kwargs.get("pdf_session_id")
        
        logger.info(f"[PDFSummaryTool] Getting summary of {pdf_session_id}")
        return get_pdf_summary(pdf_session_id)


class PDFContextRetrievalTool(BaseTool):
    """Tool for retrieving relevant context from PDF."""
    
    def __init__(self):
        super().__init__(
            name="retrieve_context",
            description="Retrieve the most relevant sections of the PDF document based on a question."
        )
    
    def _get_declaration(self) -> types.FunctionDeclaration:
        """Get the function declaration for the LLM."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "pdf_session_id": {
                        "type": "string",
                        "description": "ID of the PDF to retrieve context from"
                    },
                    "question": {
                        "type": "string",
                        "description": "Question to find relevant context for"
                    }
                },
                "required": ["pdf_session_id", "question"]
            }
        )
    
    async def run_async(self, **kwargs) -> str:
        """Execute the tool asynchronously."""
        pdf_session_id = kwargs.get("pdf_session_id")
        question = kwargs.get("question")
        
        logger.info(f"[PDFContextRetrievalTool] Retrieving context for question: {question}")
        return retrieve_relevant_context(pdf_session_id, question)


# Instantiate tools globally (singleton pattern)
pdf_search_tool = PDFSearchTool()
pdf_entity_tool = PDFEntityExtractorTool()
pdf_summary_tool = PDFSummaryTool()
pdf_context_tool = PDFContextRetrievalTool()

# List of all tools for registry and discovery
ALL_TOOLS = [pdf_search_tool, pdf_entity_tool, pdf_summary_tool, pdf_context_tool]

# Tool registry for dynamic discovery and lookup
TOOL_REGISTRY = {
    "pdf_search": pdf_search_tool,
    "extract_entities": pdf_entity_tool,
    "pdf_summary": pdf_summary_tool,
    "retrieve_context": pdf_context_tool,
}

logger.info(f"[Tool Registry] Initialized {len(TOOL_REGISTRY)} tools: {list(TOOL_REGISTRY.keys())}")


def index_pdf_on_upload(pdf_session_id: str, pdf_text: str) -> None:
    """
    Index a PDF when it's uploaded.
    Call this from routes.py after extracting PDF text.
    
    Args:
        pdf_session_id: Unique ID for the PDF
        pdf_text: Full text content
    """
    logger.info(f"[agent_tools] Indexing PDF: {pdf_session_id}")
    index_pdf_content(pdf_session_id, pdf_text)
