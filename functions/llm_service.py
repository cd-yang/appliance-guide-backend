import os
import time
from typing import Any, Dict, Generator, List

from dotenv import load_dotenv
from firebase_functions import https_fn
from flask import json
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.google_genai import GoogleGenAI

# load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def get_llm_instance():
    """Get an instance of LLM with the API key from environment variables."""
    if not GOOGLE_API_KEY:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INTERNAL,
            message="Google API key not configured in environment variables"
        )

    return GoogleGenAI(
        api_key=GOOGLE_API_KEY,
        model="gemini-2.0-flash",
    )


def format_chat_messages(messages: List[Dict[str, str]]) -> List[ChatMessage]:
    """Convert chat history from request format to LlamaIndex format."""
    formatted_messages = []
    for message in messages:
        if "role" not in message or "content" not in message:
            raise ValueError(
                "Each message must have 'role' and 'content' fields")

        role = MessageRole.USER if message["role"].lower(
        ) == "user" else MessageRole.ASSISTANT
        formatted_messages.append(ChatMessage(
            role=role, content=message["content"]))

    return formatted_messages


def get_llm_response(messages: List[ChatMessage]) -> str:
    """Get complete response from LLM based on messages."""
    try:
        llm = get_llm_instance()
        response = llm.chat(messages=messages)
        return {
            "role": response.message.role,
            "content": response.message.content,
            "timestamp": time.time()
        }
    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INTERNAL,
            message=f"Internal error: {str(e)}")


def get_llm_streaming_response(messages: List[ChatMessage]) -> Generator[Dict[str, Any], None, None]:
    """Get streaming response from LLM based on messages, yielding chunks."""
    llm = get_llm_instance()
    response_stream = llm.stream_chat(messages=messages)
    # Yield each chunk as it arrives
    for chunk in response_stream:
        if chunk is not None and chunk.delta:
            yield f"data: {json.dumps({
                "chunk": chunk.delta,
                "done": False
            })}\n\n"

    # Signal completion
    yield f"data: {json.dumps({
        "chunk": "",
        "done": True
    })}\n\n"


def process_chat_request(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Process a chat request with LLM, returning complete response."""
    formatted_messages = format_chat_messages(messages)
    response_text = get_llm_response(formatted_messages)
    return {
        "response": response_text,
        "success": True
    }


def process_streaming_chat_request(messages: List[Dict[str, str]]) -> Generator[Dict[str, Any], None, None]:
    """Process a chat request with LLM, yielding streaming response."""
    formatted_messages = format_chat_messages(messages)
    yield get_llm_streaming_response(formatted_messages)
