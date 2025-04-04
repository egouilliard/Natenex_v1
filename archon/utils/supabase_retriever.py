import logging
from typing import List, Dict, Any, Optional
from supabase import Client, create_client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import get_env_var # Assuming get_env_var is in utils.utils

# Setup logging
logger = logging.getLogger(__name__)

# Function to get Supabase client (keep if needed, otherwise remove)
def get_supabase_client() -> Optional[Client]:
    """Initializes and returns a Supabase client instance."""
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or Service Key not configured in environment variables.")
        return None
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

async def retrieve_n8n_context(supabase_client: Client, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves n8n node and credential context from Supabase based on keywords.

    Searches relevant tables (nodes, credentials) using ILIKE for partial matching
    on name and potentially other relevant fields.

    Args:
        supabase_client: An initialized Supabase client.
        keywords: A list of keywords to search for.
        limit: The maximum number of results to return.

    Returns:
        A list of dictionaries, each representing a relevant n8n node or credential.
        Returns an empty list if no context is found or an error occurs.
    """
    if not supabase_client:
        logger.error("Supabase client is not initialized.")
        return []
    if not keywords:
        logger.warning("No keywords provided for context retrieval.")
        return []

    # Prepare keywords for ILIKE ANY query (e.g., ['%keyword1%', '%keyword2%'])
    like_patterns = [f"%{kw.strip()}%" for kw in keywords if kw.strip()]
    if not like_patterns:
        logger.warning("Keywords list resulted in empty search patterns.")
        return []

    # Define a mapping for table names and relevant columns to select
    # Adjust columns as needed based on your actual table schemas
    table_columns = {
        "n8n_internal_nodes": "id, name, tools, json_data, ts_content, created_at, updated_at",
        "n8n_external_nodes": "id, name, tools, json_data, ts_content, created_at, updated_at",
        "n8n_internal_credentials": "id, name, json_data, ts_content, created_at, updated_at", # Example columns
        "n8n_external_credentials": "id, name, json_data, ts_content, created_at, updated_at"  # Example columns
    }

    # Build parts of the SQL query dynamically
    select_parts = []
    for table, columns in table_columns.items():
        # Basic search on 'name' column for all tables
        select_parts.append(
            f"""
            SELECT '{table}' AS source_table, {columns}
            FROM {table}
            WHERE name ILIKE ANY (ARRAY[{', '.join(f"'{p}'" for p in like_patterns)}])
            """
            # Potential extension: Add search on other relevant text columns (e.g., description, tools)
            # Example: OR description ILIKE ANY (ARRAY[...])
        )

    # Combine parts with UNION ALL
    full_query = " UNION ALL ".join(select_parts)
    full_query += f" LIMIT {limit};"

    try:
        logger.debug(f"Executing Supabase query: {full_query}")
        # Use rpc for executing raw SQL. Adjust if direct table access methods are preferred/possible.
        # Note: Executing raw SQL via rpc might require specific function setup or permissions in Supabase.
        # A more common approach might be separate `.select().ilike()` calls per table if raw SQL is problematic.
        # Let's assume raw SQL execution via a hypothetical `execute_sql` function or similar capability.
        # If using the standard client, you might need separate queries:
        # response_internal = await supabase_client.table("n8n_internal_nodes").select(table_columns["n8n_internal_nodes"]).ilike("name", f"%{keywords[0]}%").limit(limit).execute() # Simplified example

        # Using supabase-py's ability to execute arbitrary functions (requires function in Supabase)
        # As a fallback, we perform separate queries and combine results if raw SQL isn't directly supported easily via RPC.
        all_results = []
        for table, columns in table_columns.items():
            try:
                # Perform ILIKE ANY using Supabase filter syntax
                query = supabase_client.table(table).select(columns)
                # Build the 'or' condition for ILIKE ANY equivalent
                or_conditions = [f"name.ilike.{pattern}" for pattern in like_patterns]
                query = query.or_(",".join(or_conditions))

                response = await query.limit(limit).execute() # Use await for async
                if response.data:
                    # Add source table info for context
                    for item in response.data:
                        item['source_table'] = table
                    all_results.extend(response.data)
                # Log errors per table if needed
                # elif response.error: logger.error(f"Error querying {table}: {response.error}")

            except Exception as table_e:
                logger.error(f"Error querying table {table}: {table_e}")

        # Simple deduplication based on name and source_table (adjust if needed)
        unique_results = []
        seen = set()
        for item in all_results:
            identifier = (item.get('name'), item.get('source_table'))
            if identifier not in seen:
                unique_results.append(item)
                seen.add(identifier)

        # Apply overall limit after combining and deduplicating
        final_results = unique_results[:limit]

        logger.info(f"Retrieved {len(final_results)} context items for keywords: {keywords}")
        return final_results

    except Exception as e:
        logger.error(f"Failed to retrieve n8n context from Supabase: {e}", exc_info=True)
        return []


# --- Cleaned up section ---
# Ensure all old vector/embedding related functions are removed below this line. 