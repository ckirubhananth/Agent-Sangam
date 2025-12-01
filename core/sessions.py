import os
import uuid
from google.adk.sessions import InMemorySessionService

# === Global session service instance ===
session_service = InMemorySessionService()

def create_session_name_for_pdf(file_name: str) -> str:
    """
    Generate a stable, unique session name for each uploaded PDF.
    Uses the file name plus a short random suffix.
    Note: pass just the file name, not the full path.
    """
    base, _ = os.path.splitext(file_name)
    return f"pdf_{base}_{uuid.uuid4().hex[:8]}"

def create_session_name_for_user(user_session_id: str) -> str:
    """
    Generate a stable, unique session name for each browser/user.
    The user_session_id should come from the frontend (localStorage).
    """
    return f"user_{user_session_id}"

async def ensure_session(app_name: str, user_id: str, session_id: str):
    """
    Create or fetch a session idempotently.
    If the session already exists, return it.
    Works for both user sessions and PDF sessions.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.debug(f"[ensure_session] Attempting to create session: {session_id} for user: {user_id}")
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        logger.debug(f"[ensure_session] Created session: {session_id}")
        return session
    except Exception as create_error:
        logger.debug(f"[ensure_session] Create failed ({create_error}), trying get...")
        try:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            logger.debug(f"[ensure_session] Got existing session: {session_id}")
            return session
        except Exception as get_error:
            logger.error(f"[ensure_session] Both create and get failed. Create: {create_error}, Get: {get_error}")
            raise RuntimeError(f"Session not found: {session_id}") from get_error
