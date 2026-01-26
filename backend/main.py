"""
TOON Chat Backend - FastAPI + LangChain + Gemini
Uses standard TOON format for efficient token usage with LLMs
Includes conversation history persistence in TOON format
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Configure comprehensive logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import TOON library with fallback
try:
    from toon import encode, decode
    logger.info("✅ python-toon library loaded successfully")
    TOON_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  python-toon not installed, using JSON fallback")
    import json
    encode = lambda x: json.dumps(x)
    decode = lambda x: json.loads(x) if isinstance(x, str) else x
    TOON_AVAILABLE = False

# Startup banner
logger.info("=" * 80)
logger.info("🚀 TOON Chat Backend Starting")
logger.info(f"📦 Model: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
logger.info(f"🔧 Log Level: {LOG_LEVEL}")
logger.info(f"📊 TOON Format: {'Enabled' if TOON_AVAILABLE else 'Disabled (JSON fallback)'}")
logger.info(f"🪟 Message Window: {os.getenv('HISTORY_WINDOW_SIZE', '10')} messages")
logger.info("=" * 80)

app = FastAPI(
    title="TOON Chat API",
    description="Efficient chat API using TOON format for 30-60% token reduction",
    version="2.1.0"
)

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
logger.info(f"🌐 CORS Allowed Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat history file path
HISTORY_FILE = Path("chat_history_toon.txt")
logger.info(f"💾 History File: {HISTORY_FILE.absolute()}")


# Request/Response models with validation
class ChatRequest(BaseModel):
    """Request with TOON-encoded messages"""
    messages_toon: str = Field(..., description="TOON-encoded conversation messages")
    use_tools: bool = Field(default=False, description="Enable tool usage (future feature)")
    session_id: str = Field(default="default", description="Session identifier")

    @validator('messages_toon')
    def validate_messages_toon(cls, v):
        if not v or not v.strip():
            raise ValueError("messages_toon cannot be empty")
        return v

    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or not v.strip():
            raise ValueError("session_id cannot be empty")
        # Sanitize session_id to prevent path traversal
        return v.replace('/', '_').replace('\\', '_')


class ChatResponse(BaseModel):
    """Response with TOON-encoded content"""
    response_toon: str = Field(..., description="TOON-encoded AI response")
    history_toon: str = Field(..., description="TOON-encoded full conversation history")
    total_messages: int = Field(..., description="Total messages in history")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


# Chat history management functions
def load_chat_history(session_id: str = "default") -> List[Dict[str, str]]:
    """Load chat history from TOON file with comprehensive logging"""
    logger.debug(f"📖 Loading chat history for session: '{session_id}'")

    if not HISTORY_FILE.exists():
        logger.info(f"📝 No history file found, starting fresh session '{session_id}'")
        return []

    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            all_sessions_toon = f.read()

            if not all_sessions_toon.strip():
                logger.info(f"📝 History file is empty for session '{session_id}'")
                return []

            # Decode TOON to get all sessions
            all_history = decode(all_sessions_toon)

            # Handle both dict and list formats
            if isinstance(all_history, dict):
                history = all_history.get(session_id, [])
            else:
                history = all_history if session_id == "default" else []

            logger.info(f"✅ Loaded {len(history)} messages for session '{session_id}'")

            # Calculate and log storage efficiency
            if TOON_AVAILABLE:
                import json
                json_size = len(json.dumps(history))
                toon_size = len(encode(history))
                savings = ((json_size - toon_size) / json_size * 100) if json_size > 0 else 0
                logger.info(f"💾 Storage efficiency - JSON: {json_size}B, TOON: {toon_size}B, Savings: {savings:.1f}%")

            return history

    except Exception as e:
        logger.error(f"❌ Error loading chat history: {e}", exc_info=True)
        return []


def save_chat_history(session_id: str, messages: List[Dict[str, str]]) -> None:
    """Save chat history to TOON file with comprehensive logging"""
    logger.debug(f"💾 Saving {len(messages)} messages for session '{session_id}'")

    try:
        # Load existing history for all sessions
        all_history = {}
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    all_history = decode(content)
                    if not isinstance(all_history, dict):
                        all_history = {"default": all_history}

        # Update this session's history
        all_history[session_id] = messages

        # Encode entire structure to TOON
        all_sessions_toon = encode(all_history)

        # Save TOON to file
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.write(all_sessions_toon)

        # Calculate and log efficiency
        if TOON_AVAILABLE:
            import json
            json_size = len(json.dumps(all_history))
            toon_size = len(all_sessions_toon)
            savings = ((json_size - toon_size) / json_size * 100) if json_size > 0 else 0
            logger.info(f"✅ Saved {len(messages)} messages to TOON file")
            logger.info(f"💾 File efficiency - JSON: {json_size}B, TOON: {toon_size}B, Savings: {savings:.1f}%")
        else:
            logger.info(f"✅ Saved {len(messages)} messages to JSON file")

    except Exception as e:
        logger.error(f"❌ Error saving chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save chat history: {str(e)}")


def append_to_history(session_id: str, role: str, content: str) -> List[Dict[str, str]]:
    """Append a single message to chat history"""
    logger.debug(f"➕ Appending {role} message to session '{session_id}'")

    history = load_chat_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    save_chat_history(session_id, history)

    return history


# LLM initialization
def get_llm():
    """Initialize Gemini LLM with error handling"""
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GOOGLE_API_KEY")

    logger.debug(f"🤖 Initializing LLM: {model_name}")

    if not api_key:
        logger.error("❌ GOOGLE_API_KEY not configured!")
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY environment variable is not set"
        )

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        logger.debug(f"✅ LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initialize LLM: {str(e)}")


def prepare_messages_with_history(
    current_message: str,
    history: List[Dict[str, str]]
) -> List:
    """Prepare messages with conversation history using MessagesPlaceholder"""
    logger.debug(f"📝 Preparing messages with {len(history)} historical messages")

    # Create a prompt template with history placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Use the conversation history to provide contextual responses."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    # Convert history to LangChain message objects
    history_messages = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            history_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            history_messages.append(AIMessage(content=content))

    # Format the prompt with history and current input
    formatted_messages = prompt.format_messages(
        history=history_messages,
        input=current_message
    )

    logger.debug(f"✅ Formatted {len(formatted_messages)} total messages for LLM")
    return formatted_messages


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - accepts TOON-encoded messages, returns TOON-encoded response

    Features:
    - TOON format for 30-60% token reduction
    - Conversation history persistence
    - Message windowing for token optimization
    - Multi-session support
    """
    logger.info(f"💬 Chat request received for session '{request.session_id}'")
    request_start = datetime.now()

    try:
        # Decode TOON to get current messages
        logger.debug(f"🔍 Decoding TOON input ({len(request.messages_toon)} chars)")
        messages_data = decode(request.messages_toon)

        # Handle both dict and list formats
        if isinstance(messages_data, dict):
            current_messages = messages_data.get("messages", [])
        else:
            current_messages = messages_data

        logger.info(f"📨 Decoded {len(current_messages)} current messages")

        # Get the last user message
        user_message = None
        for msg in reversed(current_messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            logger.warning("⚠️  No user message found in request")
            raise HTTPException(status_code=400, detail="No user message found in request")

        logger.info(f"👤 User message: '{user_message[:100]}{'...' if len(user_message) > 100 else ''}'")

        # Load conversation history from TOON file
        full_history = load_chat_history(request.session_id)
        logger.info(f"📚 Loaded {len(full_history)} total messages from history")

        # MESSAGE WINDOWING - Only send recent messages to LLM
        WINDOW_SIZE = int(os.getenv("HISTORY_WINDOW_SIZE", "10"))
        recent_history = full_history[-WINDOW_SIZE:] if len(full_history) > WINDOW_SIZE else full_history

        if len(full_history) > WINDOW_SIZE:
            logger.info(f"🪟 Windowing: Sending {len(recent_history)} messages (out of {len(full_history)} total)")
            logger.info(f"💰 Token savings: Skipping {len(full_history) - len(recent_history)} older messages")
        else:
            logger.info(f"📊 Sending all {len(recent_history)} messages (under window size)")

        # Prepare messages with history
        lc_messages = prepare_messages_with_history(user_message, recent_history)

        # Get LLM and generate response
        logger.info(f"🤖 Invoking LLM...")
        llm = get_llm()
        response = await llm.ainvoke(lc_messages)

        response_preview = response.content[:100] + ('...' if len(response.content) > 100 else '')
        logger.info(f"✅ LLM response: '{response_preview}'")

        # Save user message to history
        append_to_history(request.session_id, "user", user_message)

        # Save assistant response to history
        updated_full_history = append_to_history(request.session_id, "assistant", response.content)

        logger.info(f"📝 Updated history: {len(updated_full_history)} total messages")

        # Create response object
        response_data = {
            "role": "assistant",
            "content": response.content
        }

        # Encode response to TOON
        response_toon = encode(response_data)
        history_toon = encode(updated_full_history)

        # Log TOON efficiency stats
        if TOON_AVAILABLE:
            import json
            json_size = len(json.dumps(updated_full_history))
            toon_size = len(history_toon)
            savings = ((json_size - toon_size) / json_size) * 100 if json_size > 0 else 0
            logger.info(f"📊 Transmission efficiency: JSON={json_size}B, TOON={toon_size}B, Savings={savings:.1f}%")

        # Log request duration
        duration = (datetime.now() - request_start).total_seconds()
        logger.info(f"⏱️  Request completed in {duration:.2f}s")

        return ChatResponse(
            response_toon=response_toon,
            history_toon=history_toon,
            total_messages=len(updated_full_history)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {e}", exc_info=True)
        # Return error in TOON format
        error_data = {
            "role": "assistant",
            "content": f"I encountered an error: {str(e)}. Please try again."
        }
        return ChatResponse(
            response_toon=encode(error_data),
            history_toon=encode([]),
            total_messages=0
        )


@app.get("/api/health")
async def health():
    """Health check endpoint with comprehensive system info"""
    logger.debug("🏥 Health check requested")

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
    window_size = int(os.getenv("HISTORY_WINDOW_SIZE", "10"))

    health_status = {
        "status": "healthy" if has_api_key else "degraded",
        "model": model,
        "toon_version": "standard" if TOON_AVAILABLE else "json-fallback",
        "api_key_configured": has_api_key,
        "history_file_exists": HISTORY_FILE.exists(),
        "storage_format": "TOON" if TOON_AVAILABLE else "JSON",
        "history_window_size": window_size,
        "features": [
            "conversation_history",
            "messages_placeholder",
            "toon_format" if TOON_AVAILABLE else "json_fallback",
            "toon_file_storage",
            "message_windowing",
            "multi_session"
        ],
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"🏥 Health: {health_status['status']}")
    return health_status


@app.get("/api/history/{session_id}")
async def get_history(session_id: str = "default"):
    """Get conversation history for a session"""
    logger.info(f"📖 History request for session '{session_id}'")

    try:
        history = load_chat_history(session_id)
        history_toon = encode(history)

        # Calculate storage savings
        if TOON_AVAILABLE:
            import json
            json_size = len(json.dumps(history))
            toon_size = len(history_toon)
            savings = ((json_size - toon_size) / json_size * 100) if json_size > 0 else 0
        else:
            json_size = toon_size = len(history_toon)
            savings = 0

        return {
            "session_id": session_id,
            "history_toon": history_toon,
            "total_messages": len(history),
            "storage_efficiency": {
                "json_bytes": json_size,
                "toon_bytes": toon_size,
                "savings_percent": round(savings, 1)
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str = "default"):
    """Clear conversation history for a session"""
    logger.info(f"🗑️  Clearing history for session '{session_id}'")

    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    all_history = decode(content)

                    if isinstance(all_history, dict) and session_id in all_history:
                        message_count = len(all_history[session_id])
                        del all_history[session_id]

                        with open(HISTORY_FILE, 'w', encoding='utf-8') as fw:
                            fw.write(encode(all_history))

                        logger.info(f"✅ Cleared {message_count} messages for session '{session_id}'")

        return {"status": "success", "message": f"History cleared for session '{session_id}'"}
    except Exception as e:
        logger.error(f"❌ Error clearing history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.debug("🏠 Root endpoint accessed")

    return {
        "message": "TOON Chat API - Token-Efficient AI Chat",
        "version": "2.1.0",
        "toon_enabled": TOON_AVAILABLE,
        "features": [
            "TOON format encoding/decoding" if TOON_AVAILABLE else "JSON format (TOON library not installed)",
            "Conversation history persistence",
            "LangChain MessagesPlaceholder",
            "Multi-session support",
            "Token efficiency tracking",
            "Message windowing",
            f"Storage savings: {'47% (TOON)' if TOON_AVAILABLE else 'None (JSON)'}"
        ],
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "history": "/api/history/{session_id}",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info("=" * 80)
    logger.info(f"🚀 Starting TOON Chat Backend")
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"📚 API Docs: http://{host}:{port}/docs")
    logger.info(f"💾 History stored in TOON format: {TOON_AVAILABLE}")
    logger.info("=" * 80)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
