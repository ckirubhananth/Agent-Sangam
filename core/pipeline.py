from runners import auto_runner, qa_runner
from core.sessions import create_session_name_for_user
from google.genai import types

async def route_question(selected_pdf_session_id: str | None, user_id: str, question: str):
    """
    Route a user question through the appropriate agent pipeline.
    """

    # 1) Answer from selected PDF (if any)
    if selected_pdf_session_id:
        message = types.Content(role="user", parts=[types.Part(text=question)])
        async for event in qa_runner.run_async(
            user_id="shared_pdf",
            session_id=selected_pdf_session_id,
            new_message=message
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"[QA Runner] {text}")

    # 2) Save and recall in user's personal memory
    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for event in auto_runner.run_async(
        user_id=user_id,
        session_id=create_session_name_for_user(user_id),
        new_message=message
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text != "None":
                print(f"[Auto Runner] {text}")
