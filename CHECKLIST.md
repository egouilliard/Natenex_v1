# Natenex Migration Checklist (from Archon Fork)

This checklist outlines the steps required to transform the forked Archon repository into the Natenex application, which generates n8n workflows in JSON format.

**Status:** [ ] In Progress / [ ] Completed

---

## Phase 1: Setup and Configuration (Initial Steps)

*   [X] **Verify Root Folder Name:** Confirm the project's root directory is named `Natenex`.
*   [X] **Create Virtual Environment:**
    *   Run `python3 -m venv venv` in the root directory.
*   [X] **Activate Virtual Environment:**
    *   Run `source venv/bin/activate` (macOS).
*   [X] **Install Initial Dependencies:**
    *   Run `pip install -r requirements.txt`.
*   [X] **Set Up Environment Variables (`workbench/env_vars.json`):**
    *   Access via Streamlit UI ("Environment" tab) or edit the file directly.
    *   [X] `OPENROUTER_API_KEY`: Set to your OpenRouter key.
    *   [X] `BASE_URL`: Set to `"https://openrouter.ai/api/v1"`.
    *   [X] `PRIMARY_MODEL`: Set to `"google/gemini-pro"` (or preferred Gemini model).
    *   [X] `REASONER_MODEL`: Set to `"google/gemini-pro"` (or preferred Gemini model).
    *   [X] `ADVISOR_MODEL`: Set to `"google/gemini-pro"` (or preferred model).
    *   [X] `SUPABASE_URL`: Set to your Supabase project URL.
    *   [X] `SUPABASE_SERVICE_KEY`: Set to your Supabase service key (likely `service_role` key).
    *   [X] `OPENAI_API_KEY`: Clear or remove this variable.
*   [X] **Create `.cursor-rules.json`:**
    *   Create the file in the root directory with the content provided separately.

## Phase 2: Data Handling Refactor (Core Changes)

*   [X] **Remove Documentation Crawler:**
    *   [X] Delete `archon/crawl_pydantic_ai_docs.py`.
    *   [X] Delete `streamlit_pages/documentation.py`.
    *   [X] In `streamlit_ui.py`, remove the "Documentation" tab definition.
    *   [X] In `streamlit_pages/intro.py`, remove "Step 3: Documentation Crawling" expander section and renumber subsequent steps.
    *   [X] Update `create_new_tab_button` calls in `intro.py` if needed.
*   [ ] **Adapt Supabase Interaction (`archon/utils/vector_db_utils.py` -> `archon/utils/supabase_retriever.py`):**
    *   [X] Rename the file to `supabase_retriever.py`.
    *   [ ] Update all import statements in other files referencing the old name.
    *   [X] Remove functions related to vector search, embeddings, etc.
    *   [X] **Create `retrieve_n8n_context` function:**
        *   Define `async def retrieve_n8n_context(supabase_client: Client, keywords: List[str], limit: int = 10) -> List[Dict]:`.
        *   Implement logic to construct and execute SQL queries against the relevant `n8n_*_nodes` tables using the `keywords`.
        *   **Query Strategy:** Focus searches on `n8n_internal_nodes` and `n8n_external_nodes`. Use `ILIKE ANY` on `name` and potentially `tools` (if relevant) and `ts_content` columns. Consider combining results from both tables or prioritizing based on keywords. Return relevant columns (`name`, `tools`, `ts_content`, `json_data`).
        ```sql
        -- Example Fragment (adjust table and columns as needed):
        SELECT name, tools, ts_content, json_data FROM n8n_internal_nodes
        WHERE name ILIKE ANY (ARRAY[...keywords...])
        UNION ALL -- Combine with external nodes
        SELECT name, tools, ts_content, json_data FROM n8n_external_nodes
        WHERE name ILIKE ANY (ARRAY[...keywords...])
        LIMIT limit;
        ```
        *   Ensure function handles potential errors and returns a list of dictionaries.
        *   **(Self-Correction):** Also consider retrieving credential information from `n8n_*_credentials` tables if the user query implies needing specific authentication nodes. The query logic might need to adapt based on keywords.
    *   [ ] **Update Agent Calls:** Modify agents using documentation retrieval (Primary Coder, Tools Refiner, Advisor) to:
        *   Extract relevant `keywords` from the user message/context.
        *   Call `retrieve_n8n_context(supabase_client, keywords)`.
        *   Adapt `@tool` definitions as needed.
*   [ ] **Update Database Schema Info Files:**
    *   [ ] Delete `utils/site_pages_ollama.sql` (and similar).
    *   [ ] Clear `utils/site_pages.sql` and replace with comments describing the *required* Supabase tables and columns ( `n8n_internal_nodes`, `n8n_external_nodes`, `n8n_internal_credentials`, `n8n_external_credentials` with their respective columns), explicitly stating no vector index is needed.
*   [X] **Update Database UI (`streamlit_pages/database.py`):**
    *   [X] Remove UI elements for embedding dimensions, vector indexes/functions.
    *   [X] Change UI text/buttons to focus on verifying Supabase connection and checking for the existence of the four required `n8n_*` tables.

## Phase 3: Core Logic and Agent Prompts (LLM Guidance)

*   [ ] **Rewrite Agent System Prompts:**
    *   Review and rewrite system prompts in all `*.py` files within `archon/agents/` and `archon/agents/refiners/`.
    *   [ ] **General:** Update role/goal to "n8n Workflow Engineer" / "generating n8n workflow JSON".
    *   [ ] **Context Usage:** Instruct agents how to use retrieved context ( `name`, `tools`, `ts_content`, `json_data` from node/credential tables) for generation.
    *   [ ] **Primary Coder:** Enforce outputting *only* valid n8n JSON structure. Remove Python file generation instructions.
    *   [ ] **Reasoner:** Focus planning on n8n workflow structure (triggers, nodes, data flow, credentials).
    *   [ ] **Refiners:**
        *   `Tools Refiner`: Refocus on refining n8n node parameters/connections in JSON based on `ts_content`.
        *   `Prompt Refiner`: Adapt for refining user request or generated JSON comments/clarity.
        *   `Agent Refiner`: Decide if needed. If not, remove the agent file.
*   [ ] **Adapt LangGraph Workflow (`archon/archon_graph.py`):**
    *   [ ] Update `State` definition for `retrieved_context` (list of dictionaries).
    *   [ ] Remove transitions for `Agent Refiner` if it was removed.
    *   [ ] Ensure `keywords` are extracted and `retrieved_context` is passed correctly.

## Phase 4: Output, UI, and Examples (User Facing)

*   [ ] **Handle JSON Output in UI (`streamlit_pages/chat.py`):**
    *   [ ] Ensure final workflow output is rendered using `st.json()`.
*   [ ] **UI Text & Branding Replacements:**
    *   [X] Find/replace "Archon" -> "Natenex".
    *   [X] Find/replace "Pydantic AI" -> "n8n".
    *   [X] Find/replace "Agent" (product) -> "Workflow".
    *   [X] Find/replace "Python code" (output) -> "JSON" / "workflow JSON".
    *   [ ] Replace `public/Archon.png` with a Natenex logo (update `st.image` path if needed).
*   [ ] **Populate Example Library:**
    *   [ ] Create `agent-resources/examples/n8n_workflows/`.
    *   [ ] Add example n8n `.json` workflow files.
    *   [ ] Update `archon/agents/advisor.py` to reference these examples.

## Phase 5: Final Checks and Testing (Validation)

*   [ ] **Review Dependencies (`requirements.txt`):**
    *   [ ] **Keep necessary:** `pydantic-ai`, `langgraph`, `streamlit`, `fastapi`, `uvicorn`, `supabase-py`, `requests`, `python-dotenv`, `httpx`.
    *   [ ] **Remove unnecessary:** Vector-specific libraries (`supabase-vector-client`, `hnswlib`, `pgvector`), `openai` (unless needed for OpenRouter compatibility layer).
    *   [ ] **Add if needed:** Specific `openrouter` or `google-generativeai` libraries.
    *   [ ] Finalize `requirements.txt` (manual edit or `pip freeze > requirements.txt`).
*   [ ] **Perform Iterative Testing:**
    *   [ ] Start Streamlit UI: `streamlit run streamlit_ui.py`.
    *   [ ] Configure Environment/Database via UI.
    *   [ ] Test workflow generation in the Chat tab with varied n8n requests.
    *   [ ] Debug issues related to data retrieval, prompt adherence, JSON validity, graph flow, and UI display.
    *   [ ] Refine prompts, retrieval logic, and graph as needed.

---
**Phase 6: MCP Integration (Future)**

*   [ ] Update MCP configuration (`agent-resources/mcps/`, `setup_mcp.py`) for Natenex.
*   [ ] Test MCP server (`mcp/main.py`) integration with `graph_service.py`.
*   [ ] Update MCP instructions in UI (`streamlit_pages/mcp.py`) and documentation.

---