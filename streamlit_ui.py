from __future__ import annotations
from dotenv import load_dotenv
import streamlit as st
import logfire
import asyncio

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Natenex - n8n Workflow Generator",
    page_icon="⚡",
    layout="wide",
)

# Utilities and styles
from utils.utils import get_clients
from streamlit_pages.styles import load_css

# Streamlit pages
from streamlit_pages.intro import intro_tab
from streamlit_pages.chat import chat_tab
from streamlit_pages.environment import environment_tab
from streamlit_pages.database import database_tab
from streamlit_pages.mcp import mcp_tab

# Load environment variables from .env file
load_dotenv()

# Initialize clients
openai_client, supabase = get_clients()

# Load custom CSS styles
load_css()

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire='never')

async def main():
    # Check for tab query parameter
    query_params = st.query_params
    if "tab" in query_params:
        tab_name = query_params["tab"]
        if tab_name in ["Intro", "Chat", "Environment", "Database", "MCP"]:
            st.session_state.selected_tab = tab_name

    # Add sidebar navigation
    with st.sidebar:
        st.image("public/Archon.png", width=1000)
        
        # Navigation options with vertical buttons
        st.write("### Navigation")
        
        # Initialize session state for selected tab if not present
        if "selected_tab" not in st.session_state:
            st.session_state.selected_tab = "Intro"
        
        # Vertical navigation buttons
        intro_button = st.button("Introduction", use_container_width=True, key="intro_button")
        chat_button = st.button("Workflow Chat", use_container_width=True, key="chat_button")
        env_button = st.button("Environment", use_container_width=True, key="env_button")
        db_button = st.button("Database", use_container_width=True, key="db_button")
        mcp_button = st.button("MCP Server", use_container_width=True, key="mcp_button")
        
        # Update selected tab based on button clicks
        if intro_button:
            st.session_state.selected_tab = "Intro"
        elif chat_button:
            st.session_state.selected_tab = "Chat"
        elif mcp_button:
            st.session_state.selected_tab = "MCP"
        elif env_button:
            st.session_state.selected_tab = "Environment"
        elif db_button:
            st.session_state.selected_tab = "Database"
    
    # Display the selected tab
    if st.session_state.selected_tab == "Intro":
        st.title("Natenex - Introduction")
        intro_tab()
    elif st.session_state.selected_tab == "Chat":
        st.title("Natenex - Workflow Chat")
        await chat_tab()
    elif st.session_state.selected_tab == "MCP":
        st.title("Natenex - MCP Server Configuration")
        mcp_tab()
    elif st.session_state.selected_tab == "Environment":
        st.title("Natenex - Environment Configuration")
        environment_tab()
    elif st.session_state.selected_tab == "Database":
        st.title("Natenex - Database Configuration")
        database_tab(supabase)

if __name__ == "__main__":
    asyncio.run(main())
