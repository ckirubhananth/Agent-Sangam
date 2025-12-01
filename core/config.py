import os
from google.genai import types
from google.adk.models import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

# Load environment variables from .env if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars

# === Application constants ===
APP_NAME = "AgentSangamApp"
DEFAULT_USER_ID = "kirubha"

# === Authentication (prefer env vars) ===
# Try Google AI API key first, fall back to Vertex AI (Google Cloud) settings.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION")

# === Retry configuration ===
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# === Gemini model setup ===
# The `Gemini` model can be used with the Google AI API (api_key)
# or the Google Cloud Vertex AI (vertexai=True + project/location).
# Prefer explicit GOOGLE_API_KEY if provided; otherwise require
# GOOGLE_PROJECT and GOOGLE_LOCATION for Vertex AI usage.
if GOOGLE_API_KEY:
    gemini_model = Gemini(
        model="gemini-2.5-flash-lite",
        api_key=GOOGLE_API_KEY,
        retry_options=retry_config,
    )
elif GOOGLE_PROJECT and GOOGLE_LOCATION:
    gemini_model = Gemini(
        model="gemini-2.5-flash-lite",
        vertexai=True,
        project=GOOGLE_PROJECT,
        location=GOOGLE_LOCATION,
        retry_options=retry_config,
    )
else:
    raise RuntimeError(
        "Missing Google AI configuration. Set either GOOGLE_API_KEY, "
        "or both GOOGLE_PROJECT and GOOGLE_LOCATION environment variables."
    )

# === Global services ===
# Shared across all runners to ensure consistent session and memory handling.
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
