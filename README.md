# ForgeAI Hackathon: Developing Your Application

Welcome, Hackathon Participants! This document guides you through setting up your development environment and building your custom application using the ForgeAI Default Application template.

## 1. Overview: Your Application Environment

*   **Server-Side:** Your team's application (including a dedicated chatbot app and RAG app components) runs inside a container on our servers. This container environment is where your final application will be deployed and tested.
*   **Core Stack:** The default application uses **FastAPI** for the backend API and **Streamlit** for the frontend user interface.
*   **Your Goal:** You will build custom features and logic on top of this default application template.
*   **Workflow:**
    1.  **Clone:** Get the application code onto your local machine.
    2.  **Develop Locally:** Write your backend (FastAPI) and frontend (Streamlit) code.
    3.  **Test Locally:** Run both the backend and frontend on your machine to test changes.
    4.  **Push:** Commit and push your changes to your team's designated GitHub repository. The changes pushed to the specific monitored branch will be reflected in your containerized application on the server (check with organizers for branch details).

## 2. Setting Up Your Local Development Environment

To work on the application, you need to set it up on your local machine first.

1.  **Clone the Repository:**
    *   Get the URL for your team's assigned GitHub repository.
    *   Open your terminal or command prompt.
    *   Clone the repository:
        ```bash
        git clone <your-team-repository-url>
        cd <repository-directory-name>
        ```

If you want to pull your branch in the container, come see me (Paul)

2.  **Create a Python Virtual Environment:**
    *   It's highly recommended to use a virtual environment to manage dependencies for this project.
    *   Navigate into the cloned repository directory if you haven't already.
    *   Create a virtual environment (common methods):
        ```bash
        # Using venv (built-in)
        python -m venv venv
        # Or using conda
        # conda create -n forgeai_env python=3.9 # Or desired version
        ```
    *   Activate the virtual environment:
        *   **macOS/Linux:** `source venv/bin/activate`
        *   **Windows (Git Bash):** `source venv/Scripts/activate`
        *   **Windows (CMD):** `.\venv\Scripts\activate.bat`
        *   **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
        *   **Conda:** `conda activate forgeai_env`

3.  **Install Dependencies:**
    *   Once your virtual environment is active, install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Environment Variables (API Keys, etc.):**
    *   Your application might require API keys or other configuration secrets.
    *   **DO NOT** hardcode secrets directly in your Python files.
    *   Use environment variables. You can set them in your terminal before running, or use a `.env` file managed by a library like `python-dotenv` (it's included in the default_app `requirements.txt`).
    *   Create a `.env` file in the root directory (make sure `.env` is listed in your `.gitignore` file to avoid committing secrets):
        ```.env
        MISTRAL_API_KEY="your_mistral_api_key_here"
        OTHER_VARIABLE="some_value"
        ```
    *   Load these variables in your Python code (typically near the start of `main_back.py` or where needed):
        ```python
        import os
        from dotenv import load_dotenv

        load_dotenv() # Loads variables from .env file into environment

        api_key = os.getenv("MISTRAL_API_KEY")
        ```

## 3. Understanding the Tech Stack: FastAPI & Streamlit

### FastAPI (Backend)

*   **What it is:** A modern, fast (high-performance) Python web framework for building APIs (Application Programming Interfaces). Think of it as the engine room - it handles requests, processes data, interacts with databases or external services (like AI models), and sends back responses.
*   **How it works:** You define *endpoints* (specific URLs) that your frontend or other services can call. When a request hits an endpoint, FastAPI runs the corresponding Python function, which contains your logic. It uses Python type hints for data validation and automatically generates interactive API documentation (usually at `/docs` or `/redoc`).
*   **In this project:** Your core backend logic lives here. You'll define API endpoints in `backend/routes.py` and implement the underlying functions in `backend/services.py` and `backend/utils.py`. The main entry point is `main_back.py`.
*   **Learn More:** [FastAPI Official Documentation](https://fastapi.tiangolo.com/)

### Streamlit (Frontend)

*   **What it is:** An open-source Python library that makes it easy to create and share custom web apps for machine learning and data science. It lets you build interactive UIs using simple Python scripts.
*   **How it works:** You write a standard Python script (`.py`). Streamlit runs this script from top to bottom whenever a user interacts with a widget (like a button, slider, or text input). Streamlit components (like `st.button`, `st.write`, `st.text_input`) render as interactive elements in the web browser.
*   **In this project:** This is what the user sees and interacts with. Your frontend code, located primarily within the `frontend/` folder and orchestrated by `main_front.py`, will create the UI elements (buttons, text areas, charts).
*   **Learn More:** [Streamlit Official Documentation](https://docs.streamlit.io/)

### How They Interact

The Streamlit frontend and FastAPI backend run as separate processes but work together:

1.  **User Action:** A user interacts with an element in the Streamlit UI (e.g., clicks a "Submit" button).
2.  **Streamlit Code:** Your Streamlit Python code detects this interaction.
3.  **API Call:** The Streamlit code uses a standard HTTP client library (like `requests` or `httpx`) to make a network request to a specific endpoint defined in your FastAPI backend (e.g., `http://localhost:8000/api/v1/process_data`). It sends any necessary data (like text input) in the request.
4.  **FastAPI Code:** The FastAPI backend receives the request at the specified endpoint.
5.  **Backend Logic:** The corresponding FastAPI function executes your backend logic (defined in `services.py` or `utils.py`), potentially calling external services like Mistral AI.
6.  **API Response:** FastAPI sends an HTTP response back to Streamlit, usually containing data in JSON format.
7.  **Streamlit Update:** Your Streamlit code receives the response from FastAPI.
8.  **UI Update:** Streamlit uses the received data to update the UI, displaying results, messages, or new elements to the user.

```python
# Example within Streamlit (main_front.py or frontend/ file)
import streamlit as st
import requests # Need to install 'requests' (pip install requests)

# Assuming FastAPI is running on localhost:8000
FASTAPI_BACKEND_URL = "http://localhost:8000" # Adjust if different

user_input = st.text_area("Enter your prompt:")

if st.button("Send to Backend"):
    if user_input:
        try:
            # Make POST request to a backend endpoint '/api/v1/process'
            response = requests.post(
                f"{FASTAPI_BACKEND_URL}/api/v1/process",
                json={"text": user_input} # Sending data as JSON
            )
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            # Process successful response
            result_data = response.json() # Get JSON response from backend
            st.success("Backend processed successfully!")
            st.json(result_data) # Display the result

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text.")

```

## 4. Development Workflow and Project Structure

1.  **Understand the Structure:**
    *   `main_back.py`: Main FastAPI application file. **Do not modify core server arguments here.** Imports routers.
    *   `main_front.py`: Main Streamlit application file. **Do not modify core server arguments here.** Imports UI components/logic.
    *   `backend/`: Folder for your FastAPI code.
        *   `backend/routes.py`: Define your API endpoints (routers) here.
        *   `backend/services.py`: Implement the core business logic for your endpoints.
        *   `backend/utils.py`: Place helper functions and utilities used by your backend.
    *   `frontend/`: Folder for your Streamlit UI code. Place your custom UI elements, pages, or components here and import them into `main_front.py`.
    *   `config.toml`: Configuration file for Streamlit. Follow specific rules (see below).
    *   `start.sh`: Server-side script to run the application. **DO NOT MODIFY.**
    *   `requirements.txt`: Python dependencies.
    *   `.gitignore`: Specifies files/folders intentionally untracked by Git (e.g., `venv/`, `.env`, `__pycache__/`). Make sure `.env` is in here!

2.  **Implement Your Logic:**
    *   **Backend:** Add new endpoints in `backend/routes.py`, implement the logic in `backend/services.py` or `backend/utils.py`, and ensure the router is included/registered in `main_back.py` if necessary (check existing patterns).
    *   **Frontend:** Add your Streamlit widgets, logic, and API calls within the `frontend/` folder or directly in `main_front.py`. Structure your UI logically using functions or classes imported into `main_front.py`.

3.  **Run Locally for Testing:**
    *   You need to run both the backend and frontend simultaneously. Open two separate terminals, both with the virtual environment activated.
    *   **Terminal 1 (Start FastAPI Backend):**
        ```bash
        uvicorn main_back:app --reload --host 0.0.0.0 --port 8000
        ```
        *(Check `main_back.py` or `start.sh` if a different command/port is standard)*
        *   `--reload`: Automatically restarts the server when code changes are detected.
    *   **Terminal 2 (Start Streamlit Frontend):**
        ```bash
        streamlit run main_front.py
        ```
        *(Streamlit usually runs on port 8501 by default)*
    *   Open your web browser to the local Streamlit address provided in the terminal (e.g., `http://localhost:8501`). Interact with your frontend, which should now communicate with your local backend running on port 8000.

4.  **Commit and Push:**
    *   Once you're happy with your changes:
        ```bash
        git add . # Stage all changes (or specify files)
        git commit -m "Your descriptive commit message"
        git push origin <your-branch-name> # Push to the designated branch on GitHub
        ```

## 5. Mandatory Guidelines & Constraints

**Please adhere strictly to these rules to ensure your application runs correctly in the server environment:**

*   **DO NOT MODIFY Server Arguments:** In `main_back.py` and `main_front.py`, do not change any existing arguments related to server ports, host binding (`host=`), `root_path`, or other server configuration parameters passed during application startup. These are set specifically for the container environment.
*   **DO NOT MODIFY `start.sh`:** This script is used by the server environment to launch your application correctly. Do not change it.
*   **DO NOT RENAME/DELETE Existing Directories:** Maintain the existing core directory structure (`backend/`, `frontend/`, etc.). You can *add* new directories inside `backend/` or `frontend/` or at the root level as needed for organization.
*   **`config.toml` Updates:**
    *   If you need to add Streamlit configurations to `config.toml`, you *can* do so.
    *   **Avoid modifying or adding the `[server]` block** if possible.
    *   If you absolutely must use the `[server]` block, **add it only at the very end of the `config.toml` file** to prevent conflicts with server-side configurations.
        ```toml
        # Example: Adding theme changes (OK)
        [theme]
        base = "dark"
        primaryColor = "#FF4B4B"

        # Example: Adding [server] block (ONLY if necessary, ADD AT END)
        [client]
        toolbarMode="viewer"
        # ... other non-server settings ...
        [theme]
        base = "light"

        # Add server block last if needed
        [server]
        runOnSave = true
        ```
*   **Code Placement:** Put your primary backend logic in `backend/` (`routes.py`, `services.py`, `utils.py`) and frontend logic in `frontend/`. The `main_back.py` and `main_front.py` files act as the entry points that load and orchestrate your code from these directories.

## 6. ForgeAI GenAI Services

ForgeAI offers a suite of Generative AI (GenAI) services ready for integration, including:

*   Retrieval-Augmented Generation (RAG)
*   AI Chatbots
*   And more...

To explore the full range of GenAI services and learn how to integrate them into your applications (e.g., calling them from your FastAPI backend), please refer to the **ForgeAI GenAI Services Repository:** [ForgeAI GenAI Services Repository Link Here - *Please insert the actual link*]

This repository provides comprehensive documentation on available services, how to use them via API calls, and best practices for integration.

## 7. Final Tips & Getting Help

*   Commit and push your changes frequently.
*   Test both backend and frontend locally before pushing.
*   Use clear variable names and add comments where necessary.
*   If you encounter issues or have questions, reach out to the hackathon organizers or mentors via the designated communication channel (e.g., Slack, Discord).

Happy Hacking!
