import logging
from google.adk.agents import LlmAgent
from core.config import gemini_model
from tools.agent_tools import pdf_summary_tool

logger = logging.getLogger(__name__)

# Configure Summarizer agent with tools for document summarization
summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=gemini_model,
    description="You summarize document segments into concise, meaningful text. Use pdf_summary to understand document structure and key content.",
    tools=[pdf_summary_tool]
)

logger.info("[Summarizer Agent] Initialized with 1 tool: pdf_summary")
