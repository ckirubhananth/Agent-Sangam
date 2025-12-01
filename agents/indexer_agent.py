import logging
from google.adk.agents import LlmAgent
from core.config import gemini_model
from tools.agent_tools import pdf_entity_tool, pdf_summary_tool

logger = logging.getLogger(__name__)

# Configure Indexer agent with tools for entity extraction and summarization
indexer_agent = LlmAgent(
    name="indexer_agent",
    model=gemini_model,
    description="You index documents and extract key information like entities, themes, and summaries for retrieval. Use extract_entities to find key entities and pdf_summary to understand document structure.",
    tools=[pdf_entity_tool, pdf_summary_tool]
)

logger.info("[Indexer Agent] Initialized with 2 tools: extract_entities, pdf_summary")
