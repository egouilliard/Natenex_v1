import streamlit as st
import sys
import os

# Add the parent directory to sys.path to allow importing from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils.utils import create_new_tab_button # Not used here anymore

def intro_tab():
    """Display the introduction and setup guide for Natenex"""    
    # Welcome message
    st.markdown(
        """
        Welcome to Natenex! This application helps you generate n8n workflow JSON using AI agents.
        Follow the steps below to get started.
        """
    )

    # Step 1: Environment Setup
    st.divider()
    with st.expander("**Step 1: Configure Environment Variables**", expanded=True):
        st.markdown(
            """
            - Navigate to the **Environment** tab.
            - Ensure your API keys (`OPENROUTER_API_KEY`) and other settings (`BASE_URL`, model names) are correctly configured in `workbench/env_vars.json` or via the UI.
            - Ensure your Supabase connection details (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`) are set if you intend to use the n8n context retriever.
            - Click **Save Environment Variables** if you make changes in the UI.
            - The application will automatically reload necessary components when variables change.
            """
        )

    # Step 2: Database Verification
    st.divider()
    with st.expander("**Step 2: Verify Database Connection & Schema**", expanded=False):
        st.markdown(
            """
            - Navigate to the **Database** tab.
            - **Verify Connection:** Click the "Verify Supabase Connection" button. A success message should appear if your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct.
            - **Check Required Tables:** Click the "Check for Required Natenex Tables" button. This ensures the necessary `n8n_*` tables exist in your Supabase database for context retrieval.
            - *(Note: Natenex retrieves structured data directly, it does not require vector embeddings or related database functions.)*
            """
        )

    # Step 3 (was 4): Workflow Generation
    st.divider()
    with st.expander("**Step 3: Generate n8n Workflows**", expanded=False):
        st.markdown(
            """
            - Navigate to the **Workflow Chat** tab.
            - **Start a New Workflow:** Click the "➕ New Workflow" button in the sidebar.
            - **Enter Your Request:** Describe the n8n workflow you want to build in the chat input. Be specific about the trigger, actions, data transformations, and any required credentials.
            - **Interact with the AI:** The AI agents (Reasoner, Primary Coder, Refiners) will collaborate to understand your request, plan the workflow, retrieve relevant n8n node/credential information (if needed), and generate the n8n workflow JSON.
            - **Review and Refine:** Examine the generated JSON output. Provide feedback or ask for modifications in the chat if the workflow isn't quite right.
            """
        )
        # create_new_tab_button("💬 Create New Workflow Tab", tab_type="chat", icon="➕") # This button likely belongs in the chat sidebar, not here. Let's keep the intro focused on steps.

    # Step 4 (was 5): Explore Examples & Advanced Features
    st.divider()
    with st.expander("**Step 4: Explore Examples and Advanced Features**", expanded=False):
        st.markdown(
            """
            - **Examples:** Check the `agent-resources/examples/n8n_workflows/` directory for sample n8n JSON files that Natenex can potentially generate. The Advisor agent may use these as references.
            - **Multi-Agent Collaboration Platform (MCP):** Explore the **MCP** tab for managing and potentially deploying agents as microservices (experimental).
            - **Agent States:** Observe the agent states and thought processes displayed during workflow generation in the Chat tab for better understanding and debugging.
            """
        )

    st.divider()
    st.success("You're all set! Head over to the **Environment** or **Database** tab to verify your setup, or go straight to **Workflow Chat** to start building.")

    # Resources
    st.markdown("""
    ## Additional Resources
    
    - [GitHub Repository](https://github.com/EdouardGouilliard/Natenex)
    - [Natenex Project Board](https://github.com/users/EdouardGouilliard/projects/1)
    """)