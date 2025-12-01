import logging
from google.adk.agents import LlmAgent
from core.config import gemini_model
from tools.agent_tools import pdf_search_tool, pdf_context_tool, pdf_entity_tool
from core.openapi_generator import get_openapi_generator

logger = logging.getLogger(__name__)

# Configure QA agent with tools for reasoning
# The agent will automatically choose which tools to use based on the question
qa_agent = LlmAgent(
    name="qa_agent",
    model=gemini_model,
    description="You answer user questions using indexed document knowledge. Start by searching the PDF for relevant information using pdf_search, then use retrieve_context for comprehensive answers. Always use tools to find document content before answering.",
    tools=[pdf_search_tool, pdf_context_tool, pdf_entity_tool]
)

logger.info("[QA Agent] Initialized with 3 tools: pdf_search, retrieve_context, extract_entities")

# Attach formal OpenAPI-based tool definitions for LLM function-calling support
try:
    qa_agent.tool_definitions = get_openapi_generator().get_all_tool_definitions()
    logger.info(f"[QA Agent] Attached {len(qa_agent.tool_definitions)} formal tool definitions")
except Exception:
    logger.warning("[QA Agent] Could not attach formal tool definitions")
