import os
import sys
from typing import List
from supabase import Client
import logging
import json

# Remove imports related to old RAG functions
# from openai import AsyncOpenAI (assuming it was only for embeddings)
# from archon.utils.vector_db_utils import get_embedding, list_documentation_pages, list_documentation_titles, get_page_content (or similar)


# Add parent directory for utils import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Keep necessary utils imports if any
# from utils.utils import get_env_var

logger = logging.getLogger(__name__)

# --- Remove obsolete RAG/Embedding functions ---

# async def get_embedding(text: str, client: AsyncOpenAI):
#     """Generate embedding for text using OpenAI API."""
#     # ... function body removed ...

# async def retrieve_relevant_documentation_tool(supabase: Client, embedding_client: AsyncOpenAI, user_query: str) -> str:
#     """Retrieve relevant documentation chunks based on the query with RAG."""
#     # ... function body removed ...

# async def list_documentation_pages_tool(supabase: Client) -> str:
#      """List all documentation pages available in the database."""
#      # ... function body removed ...
#
# async def get_page_content_tool(supabase: Client, page_title: str) -> str:
#      """Get the full content of a specific documentation page."""
#      # ... function body removed ...


# --- Keep any other existing, valid tools below ---

def get_file_content_tool(file_path: str) -> str:
    """Reads and returns the content of a specified file."""
    # Add basic security check to prevent accessing arbitrary files
    allowed_dirs = ["agent-resources", "workbench"] # Example allowed directories
    # Normalize paths to prevent traversal issues
    abs_file_path = os.path.abspath(file_path)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # Project root relative to this file

    is_allowed = False
    for allowed_dir in allowed_dirs:
        allowed_path = os.path.abspath(os.path.join(base_path, allowed_dir))
        if abs_file_path.startswith(allowed_path):
            is_allowed = True
            break

    if not is_allowed:
        error_msg = f"Access denied: File path '{file_path}' is outside allowed directories."
        logger.error(error_msg)
        return error_msg # Return error instead of raising?

    try:
        with open(abs_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Optional: Add limit on file size?
        return content
    except FileNotFoundError:
        error_msg = f"Error: File not found at {file_path}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.exception(error_msg) # Log full traceback
        return error_msg
