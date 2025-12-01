from google.adk.runners import Runner
from google.adk.plugins import LoggingPlugin
from core.config import APP_NAME, session_service, memory_service
from agents.auto_agent import auto_memory_agent
from agents.ingestion_agent import ingestion_agent
from agents.segmenter_agent import segmenter_agent
from agents.summarizer_agent import summarizer_agent
from agents.indexer_agent import indexer_agent
from agents.qa_agent import qa_agent
from tools.tool_registry import get_tool_registry
import logging

logger = logging.getLogger(__name__)

# === Logging plugin for observability ===
logging_plugin = LoggingPlugin()

# === Tool Registry ===
tool_registry = get_tool_registry()
logger.info(f"[Runners] Tool Registry: {tool_registry}")

# === Auto-memory runner (personal context per browser session) ===
auto_runner = Runner(
    agent=auto_memory_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,  # enables likes/dislikes and recall per user_session_id
    plugins=[logging_plugin]
)

# === Ingestion runner (extracts and stores PDF text) ===
ingestion_runner = Runner(
    agent=ingestion_agent,
    app_name=APP_NAME,
    session_service=session_service,
    plugins=[logging_plugin]
)

# === Segmenter runner (splits PDF into chapters/sections) ===
segmenter_runner = Runner(
    agent=segmenter_agent,
    app_name=APP_NAME,
    session_service=session_service,
    plugins=[logging_plugin]
)

# === Summarizer runner (summarizes chapters) ===
summarizer_runner = Runner(
    agent=summarizer_agent,
    app_name=APP_NAME,
    session_service=session_service,
    plugins=[logging_plugin]
)

# === Indexer runner (extracts entities/themes for retrieval) ===
indexer_runner = Runner(
    agent=indexer_agent,
    app_name=APP_NAME,
    session_service=session_service,
    plugins=[logging_plugin]
)

# === QA runner (answers questions using indexed PDF content) ===
qa_runner = Runner(
    agent=qa_agent,
    app_name=APP_NAME,
    session_service=session_service,
    plugins=[logging_plugin]
)

logger.info(f"""
[Runners] Pipeline initialized:
  - auto_runner: {auto_memory_agent.name} (tools: {[t.name for t in auto_memory_agent.tools]})
  - ingestion_runner: {ingestion_agent.name} (tools: {[t.name for t in ingestion_agent.tools]})
  - segmenter_runner: {segmenter_agent.name} (tools: {[t.name for t in segmenter_agent.tools]})
  - summarizer_runner: {summarizer_agent.name} (tools: {[t.name for t in summarizer_agent.tools]})
  - indexer_runner: {indexer_agent.name} (tools: {[t.name for t in indexer_agent.tools]})
  - qa_runner: {qa_agent.name} (tools: {[t.name for t in qa_agent.tools]})
""")
