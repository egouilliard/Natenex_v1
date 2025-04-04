import streamlit as st
import sys
import os
from supabase import create_client, Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import get_env_var

# @st.cache_data
# def load_sql_template():
    # """Load the SQL template file and cache it"""
    # with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "site_pages.sql"), "r") as f:
        # return f.read()

def get_supabase_sql_editor_url(supabase_url):
    """Get the URL for the Supabase SQL Editor"""
    try:
        # Extract the project reference from the URL
        # Format is typically: https://<project-ref>.supabase.co
        if '//' in supabase_url and 'supabase' in supabase_url:
            parts = supabase_url.split('//')
            if len(parts) > 1:
                domain_parts = parts[1].split('.')
                if len(domain_parts) > 0:
                    project_ref = domain_parts[0]
                    return f"https://supabase.com/dashboard/project/{project_ref}/sql/new"
        
        # Fallback to a generic URL
        return "https://supabase.com/dashboard"
    except Exception:
        return "https://supabase.com/dashboard"

# def show_manual_sql_instructions(sql, vector_dim, recreate=False):
    # """Show instructions for manually executing SQL in Supabase"""
    # ... removed ...

# List of required tables for Natenex
REQUIRED_TABLES = [
    "n8n_internal_nodes",
    "n8n_external_nodes",
    "n8n_internal_credentials",
    "n8n_external_credentials"
]

def check_table_exists(supabase: Client, table_name: str) -> bool:
    """Check if a specific table exists in Supabase."""
    try:
        # A simple query to check existence. Limit 0 prevents data transfer.
        supabase.table(table_name).select("id", count="exact").limit(0).execute()
        return True
    except Exception as e:
        # Specifically check for the "relation does not exist" error
        if "relation" in str(e) and f'"{table_name}" does not exist' in str(e):
            return False
        # Log or handle other unexpected errors if necessary
        st.warning(f"Unexpected error checking table '{table_name}': {e}")
        return False

def database_tab(supabase: Client):
    """Display the database configuration and verification interface for Natenex"""
    st.header("Database Configuration & Verification")
    st.write("Verify your Supabase connection and check for the required Natenex tables.")

    # Check if Supabase is configured
    if not supabase:
        st.error("Supabase connection details are missing. Please configure `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in the `workbench/env_vars.json` file or via the Environment tab.")
        # Display configured values if available but client creation failed
        url = get_env_var("SUPABASE_URL")
        key_set = bool(get_env_var("SUPABASE_SERVICE_KEY"))
        if url:
            st.write(f"- `SUPABASE_URL`: `{url}`")
        else:
            st.write("- `SUPABASE_URL`: Not set")
        st.write(f"- `SUPABASE_SERVICE_KEY`: {'Set (hidden)' if key_set else 'Not set'}")
        return

    # Verify Supabase Connection
    st.subheader("1. Verify Supabase Connection")
    if st.button("Verify Supabase Connection"):
        try:
            # Attempt a simple query (e.g., list tables, though that might require specific permissions)
            # A safe bet is to try listing schemas or a similar low-impact operation.
            # Fetching schemas is generally allowed even with restrictive RLS.
            response = supabase.rpc('pg_catalog.pg_namespace', {}).execute() # Example check
            # Check if response indicates success (might need adjustment based on Supabase client behavior)
            if response.data is not None: # Basic check, adjust as needed
                 st.success("✅ Successfully connected to Supabase!")
            else:
                 st.error("❌ Could connect, but connection test failed. Check permissions or Supabase status.")

        except Exception as e:
            st.error(f"❌ Failed to connect to Supabase: {e}")
            st.info("Please double-check your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in the Environment tab.")

    st.divider()

    # Check for Required Natenex Tables
    st.subheader("2. Check Required Natenex Tables")
    st.write(f"Natenex requires the following tables in your Supabase database for retrieving n8n node and credential context:")
    st.markdown(f"`{', '.join(REQUIRED_TABLES)}`")
    st.write("*(Natenex retrieves structured data directly and does not use vector embeddings or the `site_pages` table from Archon.)*")

    if st.button("Check for Required Natenex Tables"):
        missing_tables = []
        found_tables = []
        with st.spinner("Checking table status..."):
            for table in REQUIRED_TABLES:
                if check_table_exists(supabase, table):
                    found_tables.append(table)
                else:
                    missing_tables.append(table)

        if not missing_tables:
            st.success(f"✅ All required tables found: `{', '.join(found_tables)}`")
        else:
            if found_tables:
                st.warning(f"⚠️ Found tables: `{', '.join(found_tables)}`")
            st.error(f"❌ Missing required tables: `{', '.join(missing_tables)}`")
            st.info("Please ensure these tables exist in your Supabase project and contain the necessary n8n data. Refer to the Natenex setup documentation for details on creating and populating these tables.")

    # Remove Site Pages Table Setup section
    # st.subheader("Site Pages Table")
    # ... removed ...

    # Remove Vector dimensions selection
    # st.write("### Vector Dimensions")
    # ... removed ...

    # Remove SQL display and buttons
    # ... removed ...
    