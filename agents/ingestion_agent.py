import logging
from google.adk.agents import LlmAgent
from core.config import gemini_model
from tools.agent_tools import pdf_summary_tool

logger = logging.getLogger(__name__)

# Configure Ingestion agent with tools for document processing
ingestion_agent = LlmAgent(
    name="ingestion_agent",
    model=gemini_model,
    description="You ingest and process documents for further analysis, extracting key information and preparing for downstream tasks. Use pdf_summary to analyze document content.",
    tools=[pdf_summary_tool]
)

logger.info("[Ingestion Agent] Initialized with 1 tool: pdf_summary")
