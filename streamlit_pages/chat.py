from langgraph.types import Command
import streamlit as st
import uuid
import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from archon.archon_graph import agentic_flow

@st.cache_resource
def get_thread_id():
    return str(uuid.uuid4())

thread_id = get_thread_id()

async def run_agent_with_streaming(user_input: str):
    """
    Run the agent with streaming text for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # First message from user
    if len(st.session_state.messages) == 1:
        async for msg in agentic_flow.astream(
                {"latest_user_message": user_input}, config, stream_mode="custom"
            ):
                yield msg
    # Continue the conversation
    else:
        async for msg in agentic_flow.astream(
            Command(resume=user_input), config, stream_mode="custom"
        ):
            yield msg

async def chat_tab():
    """Display the chat interface for generating n8n workflows"""
    st.write("Describe the n8n workflow you want to build, and I'll generate the JSON for you.")
    st.write("Example: Create an n8n workflow triggered by a webhook that takes a customer email, looks up the customer in Stripe, and then sends a confirmation email via SendGrid.")

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Add a clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        message_type = message["type"]
        if message_type in ["human", "ai", "system"]:
            with st.chat_message(message_type):
                st.markdown(message["content"])    

    # Chat input for the user
    user_input = st.chat_input("Describe the n8n workflow you want to build...")

    if user_input:
        # We append a new request to the conversation explicitly
        st.session_state.messages.append({"type": "human", "content": user_input})
        
        # Display user prompt in the UI
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display assistant response in chat message container
        response_content = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder for updating the message
            
            # Add a spinner while loading
            with st.spinner("Natenex is generating the workflow..."):
                # Run the async generator to fetch responses
                async for chunk in run_agent_with_streaming(user_input):
                    # Handle different chunk types (dictionary for JSON, string for text)
                    if isinstance(chunk, dict):
                        # Pretty print the JSON adding it to the stream
                        current_json_str = json.dumps(chunk, indent=2)
                        response_content = f"```json\n{current_json_str}\n```" # Format as JSON block
                        message_placeholder.markdown(response_content)
                    elif isinstance(chunk, str):
                        # Append string chunks normally
                        response_content += chunk
                        message_placeholder.markdown(response_content)
                    else:
                        # Handle unexpected chunk types if necessary
                        pass # Or log a warning
        
        # Store final message (might be JSON or text)
        st.session_state.messages.append({"type": "ai", "content": response_content})