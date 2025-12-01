from google.adk.agents import LlmAgent
from google.adk.tools import preload_memory
from google.adk.models import Gemini
from google.adk.plugins.logging_plugin import LoggingPlugin

# === Gemini model (import from config if shared) ===
from core.config import gemini_model

# === Auto-save callback ===
async def auto_save_to_memory(callback_context):
    """
    Automatically save each turn to long-term memory.
    This ensures likes/dislikes and personal facts persist per user_session_id.
    """
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# === Auto-memory agent ===
auto_memory_agent = LlmAgent(
    model=gemini_model,
    name="AgentSangam",
    description="You are a helpful assistant that remembers user context and answers general questions.",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory
)
