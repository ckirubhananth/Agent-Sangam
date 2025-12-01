import logging
from google.adk.agents import LlmAgent
from core.config import gemini_model
from tools.agent_tools import pdf_summary_tool, pdf_entity_tool

logger = logging.getLogger(__name__)

# Configure Segmenter agent with tools for document analysis
segmenter_agent = LlmAgent(
    name="segmenter_agent",
    model=gemini_model,
    description="You segment documents into smaller, manageable parts (chapters, sections) for further processing. Use pdf_summary to understand document structure and pdf_entity to identify key content boundaries.",
    tools=[pdf_summary_tool, pdf_entity_tool]
)

logger.info("[Segmenter Agent] Initialized with 2 tools: pdf_summary, extract_entities")
