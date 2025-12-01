from fastapi import APIRouter, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
import fitz
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

from runners import (
    auto_runner,
    qa_runner,
    ingestion_runner,
    segmenter_runner,
    summarizer_runner,
    indexer_runner,
)
from core.sessions import create_session_name_for_pdf, ensure_session
from core.config import APP_NAME, GOOGLE_API_KEY, GOOGLE_PROJECT, GOOGLE_LOCATION
from google.genai import types
import google.generativeai as genai
from tools.agent_tools import index_pdf_on_upload
from tools.tool_registry import get_tool_registry, generate_tools_schema
from core.mcp_server import get_mcp_server, initialize_mcp_server
from core.openapi_generator import get_openapi_generator, initialize_openapi_generator

# Configure genai with API key if available
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialize MCP Server
mcp_server = initialize_mcp_server()
logger.info(f"[Routes] MCP Server initialized: {mcp_server.get_server_info()}")

# Initialize OpenAPI Generator
openapi_generator = initialize_openapi_generator()
logger.info(f"[Routes] OpenAPI Generator initialized with {len(openapi_generator.tools)} tools")

router = APIRouter()

# Initialize tool registry
tool_registry = get_tool_registry()
logger.info(f"[Routes] Tool Registry initialized: {tool_registry}")

# === In-memory stores ===
# Global store for uploaded PDFs (shared across browsers):
# { pdf_session_id: {pdf_name, status, text} }
global_pdfs = {}
# Per-browser conversational history for general chats: { user_session_id: [ {q, a}, ... ] }
user_histories = {}
# Per-browser, per-pdf conversational history (private to each browser):
# { user_session_id: { pdf_session_id: [ {q, a}, ... ] } }
user_pdf_histories = {}

# === Background task tracking ===
# { task_id: {status, progress, pdf_session_id, pdf_name, error, created_at, completed_at} }
background_tasks = {}

# How many previous turns to include in context
HISTORY_TURNS = 6

def extract_pdf_text(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = "".join([page.get_text() for page in doc])
    doc.close()
    return text

def process_pdf_background_sync(task_id: str, file_path: str, pdf_session_id: str, pdf_name: str):
    """Sync wrapper for background task execution (called by FastAPI BackgroundTasks)."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_pdf_background(task_id, file_path, pdf_session_id, pdf_name))
    finally:
        loop.close()

async def process_pdf_background(task_id: str, file_path: str, pdf_session_id: str, pdf_name: str):
    """Background task to process PDF: extract text, run pipeline steps."""
    try:
        logger.info(f"[Background Task {task_id}] Starting PDF processing for {pdf_name}")
        background_tasks[task_id]["status"] = "processing"
        background_tasks[task_id]["progress"] = 10

        # Extract PDF text
        logger.info(f"[Background Task {task_id}] Extracting PDF text...")
        full_text = extract_pdf_text(file_path)
        logger.info(f"[Background Task {task_id}] Extracted {len(full_text)} characters")
        background_tasks[task_id]["progress"] = 20

        # Index PDF content for tool usage
        logger.info(f"[Background Task {task_id}] Indexing PDF content...")
        index_pdf_on_upload(pdf_session_id, full_text)
        logger.info(f"[Background Task {task_id}] PDF indexed successfully")

        # Store PDF metadata in global store
        global_pdfs[pdf_session_id] = {
            "pdf_name": pdf_name,
            "status": "uploaded",
            "text": full_text,
        }

        # Run ingestion pipeline
        try:
            logger.info(f"[Background Task {task_id}] Running ingestion pipeline...")
            ingested = await run_once_and_capture(
                ingestion_runner,
                user_id="shared_pdf",
                session_id=pdf_session_id,
                prompt=f"Ingested document content:\n{full_text[:2000]}"
            )
            global_pdfs[pdf_session_id]["status"] = "ingested"
            background_tasks[task_id]["progress"] = 35
            logger.info(f"[Background Task {task_id}] Ingestion complete")
        except Exception as e:
            logger.warning(f"[Background Task {task_id}] Ingestion failed (continuing): {str(e)}")
            global_pdfs[pdf_session_id]["status"] = "ingested"
            background_tasks[task_id]["progress"] = 35

        # Run segmentation pipeline
        try:
            logger.info(f"[Background Task {task_id}] Running segmenter pipeline...")
            segmented = await run_once_and_capture(
                segmenter_runner,
                user_id="shared_pdf",
                session_id=pdf_session_id,
                prompt="Segment the ingested book into chapters and sections with years, key events, and important figures"
            )
            global_pdfs[pdf_session_id]["status"] = "segmented"
            background_tasks[task_id]["progress"] = 50
            logger.info(f"[Background Task {task_id}] Segmentation complete")
        except Exception as e:
            logger.warning(f"[Background Task {task_id}] Segmentation failed (continuing): {str(e)}")
            global_pdfs[pdf_session_id]["status"] = "segmented"
            background_tasks[task_id]["progress"] = 50

        # Run summarization pipeline
        try:
            logger.info(f"[Background Task {task_id}] Running summarizer pipeline...")
            summarized = await run_once_and_capture(
                summarizer_runner,
                user_id="shared_pdf",
                session_id=pdf_session_id,
                prompt="Summarize each chapter with years, key events, and important figures"
            )
            global_pdfs[pdf_session_id]["status"] = "summarized"
            background_tasks[task_id]["progress"] = 65
            logger.info(f"[Background Task {task_id}] Summarization complete")
        except Exception as e:
            logger.warning(f"[Background Task {task_id}] Summarization failed (continuing): {str(e)}")
            global_pdfs[pdf_session_id]["status"] = "summarized"
            background_tasks[task_id]["progress"] = 65

        # Run indexing pipeline
        try:
            logger.info(f"[Background Task {task_id}] Running indexer pipeline...")
            indexed = await run_once_and_capture(
                indexer_runner,
                user_id="shared_pdf",
                session_id=pdf_session_id,
                prompt="Index the book for entities and themes for retrieval"
            )
            global_pdfs[pdf_session_id]["status"] = "indexed"
            background_tasks[task_id]["progress"] = 100
            logger.info(f"[Background Task {task_id}] Indexing complete")
        except Exception as e:
            logger.warning(f"[Background Task {task_id}] Indexing failed (continuing): {str(e)}")
            global_pdfs[pdf_session_id]["status"] = "indexed"
            background_tasks[task_id]["progress"] = 100

        # Mark task as completed
        background_tasks[task_id]["status"] = "completed"
        background_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"[Background Task {task_id}] PDF processing completed successfully")

    except Exception as e:
        logger.error(f"[Background Task {task_id}] Failed: {str(e)}", exc_info=True)
        background_tasks[task_id]["status"] = "failed"
        background_tasks[task_id]["error"] = str(e)
        background_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
        if pdf_session_id in global_pdfs:
            global_pdfs[pdf_session_id]["status"] = "error"

async def call_gemini_direct(prompt: str) -> str:
    """Call Gemini directly using the genai client."""
    try:
        logger.debug(f"[call_gemini_direct] Calling Gemini with prompt length: {len(prompt)}")
        
        # Use genai.GenerativeModel to create a model instance and generate content
        # API key is already configured via genai.configure() in routes.py module level
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        
        # Extract text from response
        full_text = ""
        if isinstance(response, str):
            full_text = response
        elif hasattr(response, 'text') and response.text:
            full_text = response.text
        elif hasattr(response, 'content') and hasattr(response.content, 'parts') and response.content.parts:
            full_text = response.content.parts[0].text
        elif hasattr(response, 'candidates') and response.candidates:
            full_text = response.candidates[0].content.parts[0].text
        
        if not full_text:
            logger.warning("[call_gemini_direct] No text in response, response type: " + str(type(response)))
            full_text = "No response from model"
        
        logger.info(f"[call_gemini_direct] Got response: {full_text[:100]}...")
        return full_text
    except Exception as e:
        logger.error(f"[call_gemini_direct] Failed: {str(e)}", exc_info=True)
        raise

async def run_once_and_capture(runner, user_id: str, session_id: str, prompt: str) -> str:
    """Run a runner with a prompt and capture the text response."""
    logger.debug(f"[run_once_and_capture] Running {runner} for user={user_id}, session={session_id}")
    
    last_text = None
    try:
        # Ensure session exists before running
        await ensure_session(APP_NAME, user_id=user_id, session_id=session_id)
        logger.debug(f"[run_once_and_capture] Session ensured: {session_id}")
        
        # new_message expects a Content object with role and parts
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            if event.content and event.content.parts:
                t = event.content.parts[0].text
                if t and t != "None":
                    last_text = t
                    logger.debug(f"[run_once_and_capture] Captured text: {t[:100]}...")
    except Exception as e:
        logger.error(f"[run_once_and_capture] Runner failed: {str(e)}", exc_info=True)
        raise
    
    return last_text or ""

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), request: Request = None, background_tasks_runner: BackgroundTasks = None):
    user_session_id = None
    pdf_session_id = None
    task_id = None
    
    try:
        user_session_id = request.query_params.get("user_session_id") or str(uuid.uuid4())
        logger.info(f"[/upload] Starting upload for user: {user_session_id}, file: {file.filename}")

        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"[/upload] File saved to: {file_path}")

        pdf_session_id = create_session_name_for_pdf(file.filename)
        task_id = str(uuid.uuid4())
        
        logger.info(f"[/upload] Created PDF session ID: {pdf_session_id}, Task ID: {task_id}")

        # Create both sessions
        logger.info(f"[/upload] Creating shared_pdf session...")
        await ensure_session(APP_NAME, user_id="shared_pdf", session_id=pdf_session_id)
        logger.info(f"[/upload] Created shared_pdf session successfully")

        logger.info(f"[/upload] Creating user session...")
        await ensure_session(APP_NAME, user_id=user_session_id, session_id=user_session_id)
        logger.info(f"[/upload] Created user session successfully")

        # Register background task
        background_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "pdf_session_id": pdf_session_id,
            "pdf_name": file.filename,
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
        logger.info(f"[/upload] Registered background task: {task_id}")

        # Add processing task to FastAPI's background tasks (non-blocking)
        if background_tasks_runner:
            background_tasks_runner.add_task(
                process_pdf_background_sync,
                task_id,
                file_path,
                pdf_session_id,
                file.filename
            )

        # Return immediately with task_id
        logger.info(f"[/upload] Returning 200 with task_id: {task_id}")
        return JSONResponse(status_code=200, content={
            "status": "accepted",
            "task_id": task_id,
            "pdf_session_id": pdf_session_id,
            "pdf_name": file.filename,
            "user_session_id": user_session_id,
            "message": "PDF processing started in background. Check /task_status/{task_id} for progress."
        })

    except Exception as e:
        logger.error(f"[/upload] Exception during upload: {str(e)}", exc_info=True)
        if task_id and task_id in background_tasks:
            background_tasks[task_id]["status"] = "failed"
            background_tasks[task_id]["error"] = str(e)
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background PDF processing task."""
    if task_id not in background_tasks:
        return JSONResponse(
            content={"error": "Task not found"},
            status_code=404
        )
    
    task = background_tasks[task_id]
    logger.info(f"[/task_status] Fetching status for task: {task_id}, status: {task['status']}, progress: {task['progress']}")
    
    return JSONResponse(content={
        "task_id": task_id,
        "status": task["status"],  # pending, processing, completed, failed
        "progress": task["progress"],  # 0-100
        "pdf_session_id": task["pdf_session_id"],
        "pdf_name": task["pdf_name"],
        "error": task["error"],
        "created_at": task["created_at"],
        "completed_at": task["completed_at"]
    })

@router.get("/sessions")
async def list_sessions(request: Request):
    # Return all uploaded PDFs (shared across browsers)
    return JSONResponse(content=[
        {
            "session_id": sid,
            "pdf_name": meta["pdf_name"],
            "status": meta.get("status", "uploaded"),
        }
        for sid, meta in global_pdfs.items()
    ])

@router.get("/session_status")
async def session_status(request: Request):
    pdf_session_id = request.query_params.get("pdf_session_id")
    exists = pdf_session_id in global_pdfs
    return JSONResponse(content={"exists": exists})

@router.post("/ask")
async def ask_agent(request: Request):
    data = await request.json()
    question = data.get("question")
    pdf_session_id = data.get("pdf_session_id")
    user_session_id = data.get("user_session_id") or str(uuid.uuid4())

    if not question:
        return JSONResponse(content={"error": "Missing question"}, status_code=400)

    try:
        logger.info(f"[/ask] Processing question: {question[:50]}... for user: {user_session_id}")

        if pdf_session_id and pdf_session_id in global_pdfs:
            # Use stored PDF text and per-browser Q/A turns for context
            pdf_meta = global_pdfs[pdf_session_id]
            doc_text = pdf_meta["text"]
            
            # Use tool to retrieve most relevant context
            from tools.agent_tools import retrieve_relevant_context
            relevant_context = retrieve_relevant_context(pdf_session_id, question, max_chars=2000)
            
            # Fallback: if no relevant context found, use beginning of document
            if not relevant_context or relevant_context == "No relevant context found in PDF.":
                logger.info(f"[/ask] No relevant context found, using document beginning as fallback")
                relevant_context = doc_text[:2000]
            
            # Get per-browser per-pdf history
            per_pdf_histories = user_pdf_histories.setdefault(user_session_id, {})
            history = per_pdf_histories.setdefault(pdf_session_id, [])
            # Build history text (last N turns)
            turns = history[-HISTORY_TURNS:]
            history_text = "".join([f"User: {t['q']}\nAssistant: {t['a']}\n\n" for t in turns])

            prompt = (
                "You are a helpful assistant. Use the document and the conversation history to answer the question.\n\n"
                f"Conversation so far:\n{history_text}\n"
                f"Relevant document excerpt:\n{relevant_context}\n\n"
                f"Question: {question}\n\nAnswer:"
            )
            logger.info(f"[/ask] Querying PDF: {pdf_session_id} (including {len(turns)} historical turns) for user {user_session_id}")
            answer_text = await call_gemini_direct(prompt)
            # Append to per-browser pdf history
            try:
                history.append({"q": question, "a": answer_text})
            except Exception:
                logger.warning("[/ask] Failed to append to per-browser pdf history")
        else:
            # General query without PDF context — keep per-user history
            logger.info(f"[/ask] General query for user: {user_session_id}")
            history = user_histories.setdefault(user_session_id, [])
            turns = history[-HISTORY_TURNS:]
            history_text = "".join([f"User: {t['q']}\nAssistant: {t['a']}\n\n" for t in turns])
            prompt = ("You are a helpful assistant. Use the conversation history to answer the question.\n\n"
                      f"Conversation so far:\n{history_text}\nQuestion: {question}\n\nAnswer:")
            answer_text = await call_gemini_direct(prompt)
            # Append to user history
            try:
                history.append({"q": question, "a": answer_text})
            except Exception:
                logger.warning("[/ask] Failed to append to user history")

        logger.info(f"[/ask] Query complete, answer length: {len(answer_text) if answer_text else 0}")
        return JSONResponse(content={
            "question": question,
            "answer": answer_text
        })
    
    except Exception as e:
        logger.error(f"[/ask] Exception in ask_agent: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "question": question}
        )

@router.get("/tools/registry")
async def get_tools_registry():
    """Get information about all registered tools for agent discovery."""
    registry = get_tool_registry()
    return JSONResponse(content={
        "total_tools": len(registry),
        "tools": registry.get_all_tool_names(),
        "metadata": registry.get_all_metadata(),
        "schema": generate_tools_schema(),
    })

@router.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific tool."""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        return JSONResponse(
            status_code=404,
            content={"error": f"Tool '{tool_name}' not found"}
        )
    
    metadata = tool_registry.get_tool_metadata(tool_name)
    return JSONResponse(content={
        "name": tool_name,
        "metadata": metadata,
    })

@router.get("/")
async def root():
    return JSONResponse(content={"message": "Welcome to Agent Sangam Web App. Visit /static/index.html for UI."})

# === MCP Server Routes ===
@router.get("/mcp/info")
async def mcp_server_info():
    """Get MCP server information and capabilities."""
    server = get_mcp_server()
    return JSONResponse(content=server.get_server_info())

@router.get("/mcp/tools")
async def mcp_list_tools():
    """List all available tools in MCP format."""
    server = get_mcp_server()
    return JSONResponse(content={
        "tools": server.get_tools(),
        "totalTools": len(server.tools)
    })

@router.get("/mcp/tools/{tool_name}")
async def mcp_get_tool(tool_name: str):
    """Get detailed information about a specific MCP tool."""
    server = get_mcp_server()
    tool = server.get_tool(tool_name)
    if not tool:
        return JSONResponse(
            status_code=404,
            content={"error": f"Tool '{tool_name}' not found in MCP server"}
        )
    return JSONResponse(content=tool.to_dict())

@router.post("/mcp/tools/{tool_name}/call")
async def mcp_call_tool(tool_name: str, request: Request):
    """
    Call a tool through MCP interface.
    
    This endpoint provides standardized tool invocation through the Model Context Protocol,
    allowing external agents and tools to leverage PDF capabilities.
    """
    try:
        data = await request.json()
        logger.info(f"[MCP] Calling tool '{tool_name}' with params: {list(data.keys())}")
        
        # Import tools
        from tools.agent_tools import (
            PDFSearchTool, PDFEntityExtractorTool, 
            PDFSummaryTool, PDFContextRetrievalTool
        )
        
        pdf_session_id = data.get("pdf_session_id")
        if not pdf_session_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: pdf_session_id"}
            )
        
        # Route to appropriate tool
        result = None
        
        if tool_name == "pdf_search":
            query = data.get("query")
            max_results = data.get("max_results", 5)
            if not query:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required parameter: query"}
                )
            
            tool = PDFSearchTool()
            result = await tool.run_async(
                pdf_session_id=pdf_session_id,
                query=query,
                max_results=max_results
            )
            logger.info(f"[MCP] pdf_search returned {len(result) if result else 0} results")
        
        elif tool_name == "extract_entities":
            tool = PDFEntityExtractorTool()
            result = await tool.run_async(pdf_session_id=pdf_session_id)
            logger.info(f"[MCP] extract_entities returned entities")
        
        elif tool_name == "pdf_summary":
            tool = PDFSummaryTool()
            result = await tool.run_async(pdf_session_id=pdf_session_id)
            logger.info(f"[MCP] pdf_summary returned summary")
        
        elif tool_name == "retrieve_context":
            question = data.get("question")
            if not question:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required parameter: question"}
                )
            
            tool = PDFContextRetrievalTool()
            result = await tool.run_async(
                pdf_session_id=pdf_session_id,
                question=question
            )
            logger.info(f"[MCP] retrieve_context returned context")
        
        else:
            return JSONResponse(
                status_code=404,
                content={"error": f"Unknown tool: {tool_name}"}
            )
        
        return JSONResponse(content={
            "tool": tool_name,
            "status": "success",
            "result": result
        })
    
    except Exception as e:
        logger.error(f"[MCP] Error calling tool '{tool_name}': {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "tool": tool_name}
        )

@router.get("/mcp/resources")
async def mcp_list_resources():
    """List all available resources in MCP format."""
    server = get_mcp_server()
    return JSONResponse(content={
        "resources": server.get_resources(),
        "totalResources": len(server.resources)
    })

@router.get("/mcp/schema")
async def mcp_openapi_schema():
    """Get OpenAPI schema for all MCP tools."""
    server = get_mcp_server()
    return JSONResponse(content=server.generate_openapi_schema())

# === OpenAPI Tools Routes ===
@router.get("/openapi/spec")
async def get_openapi_spec():
    """Get complete OpenAPI 3.0 specification for all tools."""
    generator = get_openapi_generator()
    spec = generator.generate_openapi_spec()
    return JSONResponse(content=spec)

@router.get("/openapi/tools")
async def get_openapi_tools():
    """Get formal OpenAPI tool definitions."""
    generator = get_openapi_generator()
    tools = generator.get_all_tool_definitions()
    return JSONResponse(content={
        "tools": tools,
        "totalTools": len(tools),
        "format": "OpenAPI function definitions for LLM/Agent use"
    })

@router.get("/openapi/tools/{tool_name}")
async def get_openapi_tool(tool_name: str):
    """Get OpenAPI definition for a specific tool."""
    generator = get_openapi_generator()
    
    # Try to get as tool definition (for agent use)
    tool_def = generator.get_tool_definition(tool_name)
    if tool_def:
        return JSONResponse(content=tool_def)
    
    # Try to get as schema (for documentation)
    schema = generator.get_tool_schema(tool_name)
    if schema:
        return JSONResponse(content=schema)
    
    return JSONResponse(
        status_code=404,
        content={"error": f"Tool '{tool_name}' not found"}
    )

@router.get("/openapi/json")
async def download_openapi_json():
    """Download OpenAPI specification as JSON."""
    generator = get_openapi_generator()
    spec = generator.generate_openapi_spec()
    
    return JSONResponse(
        content=spec,
        headers={
            "Content-Disposition": "attachment; filename=openapi.json"
        }
    )

@router.get("/openapi/validate")
async def validate_openapi_spec():
    """Validate that OpenAPI spec is well-formed."""
    try:
        generator = get_openapi_generator()
        spec = generator.generate_openapi_spec()
        
        # Basic validation checks
        assert spec.get("openapi") == "3.0.0", "Invalid OpenAPI version"
        assert "info" in spec, "Missing info object"
        assert "paths" in spec, "Missing paths object"
        assert len(spec["paths"]) == 4, "Expected 4 tool paths"
        
        return JSONResponse(content={
            "valid": True,
            "message": "OpenAPI spec is valid",
            "version": spec.get("openapi"),
            "toolCount": len(spec["paths"]),
            "schemaCount": len(spec.get("components", {}).get("schemas", {}))
        })
    except Exception as e:
        logger.error(f"[OpenAPI] Validation failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "valid": False,
                "error": str(e)
            }
        )
