import streamlit as st
import platform
import json
import os

def get_paths():
    # Get the absolute path to the current directory
    base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Determine the correct python path based on the OS
    if platform.system() == "Windows":
        python_path = os.path.join(base_path, 'venv', 'Scripts', 'python.exe')
    else:  # macOS or Linux
        python_path = os.path.join(base_path, 'venv', 'bin', 'python')
    
    # Assumes mcp_server.py is still the entry point for the MCP server in the mcp directory
    server_script_path = os.path.join(base_path, 'mcp', 'mcp_server.py') # TODO: Verify mcp_server.py path/name

    return python_path, server_script_path

def generate_mcp_config(ide_type, python_path, server_script_path):
    """
    Generate MCP configuration for Natenex for the selected IDE type.
    """
    # Define server name and docker image potentially using Natenex branding if desired
    mcp_server_name = "natenex" # Changed from "archon"
    docker_image_name = "natenex-mcp:latest" # TODO: Verify Docker image name

    # Create the config dictionary for Python
    python_config = {
        "mcpServers": {
            mcp_server_name: { # Use updated server name
                "command": python_path,
                "args": [server_script_path]
            }
        }
    }
    
    # Create the config dictionary for Docker
    docker_config = {
        "mcpServers": {
            mcp_server_name: { # Use updated server name
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "--add-host=host.docker.internal:host-gateway",
                    "-e",
                    "GRAPH_SERVICE_URL", # Keep env var name consistent with graph_service expectation
                    docker_image_name # Use updated image name
                ],
                "env": {
                    "GRAPH_SERVICE_URL": "http://host.docker.internal:8100" # Assumes graph_service runs on 8100
                }
            }
        }
    }
    
    # Return appropriate configuration based on IDE type (update commands)
    if ide_type == "Windsurf":
        return json.dumps(python_config, indent=2), json.dumps(docker_config, indent=2)
    elif ide_type == "Cursor":
        # Construct the command string for Cursor
        python_cmd = f"{python_path} {server_script_path}"
        docker_cmd = f"docker run -i --rm --add-host=host.docker.internal:host-gateway -e GRAPH_SERVICE_URL=http://host.docker.internal:8100 {docker_image_name}"
        return python_cmd, docker_cmd
    elif ide_type == "Cline/Roo Code":
        return json.dumps(python_config, indent=2), json.dumps(docker_config, indent=2)
    elif ide_type == "Claude Code":
         # Construct the command strings for Claude Code add
        python_claude_cmd = f"claude mcp add {mcp_server_name.capitalize()} {python_path} {server_script_path}"
        docker_claude_cmd = f"claude mcp add {mcp_server_name.capitalize()} docker run -i --rm --add-host=host.docker.internal:host-gateway -e GRAPH_SERVICE_URL=http://host.docker.internal:8100 {docker_image_name}"
        return python_claude_cmd, docker_claude_cmd # Return the full claude commands
    else:
        return "Unknown IDE type selected", "Unknown IDE type selected"

def mcp_tab():
    """Display the Natenex MCP configuration interface""" # Updated docstring
    st.header("MCP Server Configuration") # Keep header MCP specific
    st.write("Select your AI IDE to get the appropriate MCP configuration for Natenex:") # Updated text
    
    # IDE selection with side-by-side buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        windsurf_button = st.button("Windsurf", use_container_width=True, key="windsurf_button")
    with col2:
        cursor_button = st.button("Cursor", use_container_width=True, key="cursor_button")
    with col3:
        cline_button = st.button("Cline/Roo Code", use_container_width=True, key="cline_button")
    with col4:
        claude_button = st.button("Claude Code", use_container_width=True, key="claude_button")
    
    # Initialize session state for selected IDE if not present
    if "selected_ide" not in st.session_state:
        st.session_state.selected_ide = None
    
    # Update selected IDE based on button clicks
    if windsurf_button:
        st.session_state.selected_ide = "Windsurf"
    elif cursor_button:
        st.session_state.selected_ide = "Cursor"
    elif cline_button:
        st.session_state.selected_ide = "Cline/Roo Code"
    elif claude_button:
        st.session_state.selected_ide = "Claude Code"
    
    # Display configuration if an IDE is selected
    if st.session_state.selected_ide:
        selected_ide = st.session_state.selected_ide
        st.subheader(f"MCP Configuration for {selected_ide}")
        python_path, server_script_path = get_paths()
        python_config, docker_config = generate_mcp_config(selected_ide, python_path, server_script_path)
        
        # Configuration type tabs
        config_tab1, config_tab2 = st.tabs(["Docker Configuration", "Python Configuration"])
        
        with config_tab1:
            st.markdown("### Docker Configuration")
            # Adjust language based on what generate_mcp_config returns for Claude Code
            if selected_ide == "Claude Code":
                st.code(docker_config, language="bash") # Show as shell command
            else:
                st.code(docker_config, language="json" if selected_ide != "Cursor" else None) # Show as JSON or plain text
            
            st.markdown("#### Requirements:")
            st.markdown("- Docker installed")
            st.markdown("- Run the setup script to build and start both containers (graph service and MCP server):") # Updated text
            st.code("python run_docker.py", language="bash") # TODO: Verify run_docker.py script functionality
        
        with config_tab2:
            st.markdown("### Python Configuration")
             # Adjust language based on what generate_mcp_config returns for Claude Code
            if selected_ide == "Claude Code":
                st.code(python_config, language="bash") # Show as shell command
            else:
                st.code(python_config, language="json" if selected_ide != "Cursor" else None) # Show as JSON or plain text
            
            st.markdown("#### Requirements:")
            st.markdown("- Python 3.11+ installed")
            st.markdown("- Virtual environment created and activated (`source venv/bin/activate`)") # Added activation command example
            st.markdown("- All dependencies installed via `pip install -r requirements.txt`")
            st.markdown("- Must be running Natenex not within a container") # Updated text
            st.markdown("- The Natenex Agent Service (graph_service.py) must be running separately (you can start it from the Agent Service tab).") # Added requirement note
        
        # Instructions based on IDE type
        st.markdown("---")
        st.markdown("### Setup Instructions")
        
        # Update references to "Archon" and server names/commands
        server_display_name = "Natenex" # Changed from Archon
        
        if selected_ide == "Windsurf":
            st.markdown("""
            #### How to use in Windsurf:
            1. Click on the hammer icon above the chat input
            2. Click on "Configure"
            3. Paste the JSON from your preferred configuration tab above (Docker or Python)
            4. Click "Refresh" next to "Configure"
            """)
        elif selected_ide == "Cursor":
             # Use the generated command strings directly
            python_cmd_cursor, docker_cmd_cursor = generate_mcp_config(selected_ide, python_path, server_script_path)
            st.markdown(f"""
            #### How to use in Cursor:
            1. Go to Cursor Settings > Features > MCP
            2. Click on "+ Add New MCP Server"
            3. Name: `{server_display_name}`
            4. Type: command (equivalent to stdio)
            5. Command:
                - For Python config: `{python_cmd_cursor}`
                - For Docker config: `{docker_cmd_cursor}`
            """)
        elif selected_ide == "Cline/Roo Code":
            st.markdown("""
            #### How to use in Cline or Roo Code:
            1. From the Cline/Roo Code extension, click the "MCP Server" tab
            2. Click the "Edit MCP Settings" button
            3. The MCP settings file should be displayed in a tab in VS Code
            4. Paste the JSON from your preferred configuration tab above (Docker or Python)
            5. Cline/Roo Code will automatically detect and start the MCP server named `natenex`.
            """) # Updated server name reference
        elif selected_ide == "Claude Code":
             # Use the generated command strings directly
             python_claude_cmd, docker_claude_cmd = generate_mcp_config(selected_ide, python_path, server_script_path)
             st.markdown(f"""
            #### How to use in Claude Code:
            1. Ensure the Natenex agent service (`graph_service.py`) is running if using the Python configuration. If using Docker, ensure `run_docker.py` has been executed successfully.
            2. Open a terminal and navigate to your work folder.
            3. Execute the command corresponding to your chosen configuration:

                ```bash
                # Docker Command:
                {docker_claude_cmd}

                # Python Command:
                {python_claude_cmd}
                ```
            4. Start Claude Code with the command `claude`.
            5. When Claude Code starts, at the bottom of the welcome section will be a listing of connected MCP Services. `{server_display_name}` should be listed with a status of _connected_.
            6. You can now use the `{server_display_name}` MCP service in your Claude Code projects.

            (NOTE: If you close the terminal, or start a session in a new terminal, you may need to re-add the MCP service using the `claude mcp add...` command.)
            """) # Updated service name and instructions