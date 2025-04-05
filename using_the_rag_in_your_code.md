# Integrating the ForgeAI RAG API into Your Application

This guide explains the logic behind the ForgeAI RAG (Retrieval-Augmented Generation) API and demonstrates how to use its key features within your FastAPI backend to build applications that can answer questions based on provided documents.

**The Goal:** Instead of just relying on the general knowledge of a Large Language Model (LLM), RAG allows the LLM to access and use information from specific documents you provide. This makes its answers more accurate, relevant to your specific context, and up-to-date.

## Understanding the RAG Workflow

The ForgeAI RAG API facilitates the following core workflow:

1.  **Organize Knowledge (`Collections`):** You first create logical containers called "collections" to store related documents. Think of a collection as a dedicated knowledge base for a specific topic or purpose (e.g., 'hackathon_rules', 'project_documentation').
    *   *Relevant Endpoints:* `POST /api/app/collection/new`, `GET /api/app/collection/list`, `DELETE /api/app/collection/delete`

2.  **Add Documents (`Indexing`):** You upload your documents (PDFs, text files, etc.) into a specific collection. The RAG API automatically performs several crucial steps behind the scenes:
    *   **Loads:** Reads the content of your document.
    *   **Chunks:** Breaks the document down into smaller, manageable pieces (chunks).
    *   **Embeds:** Converts each chunk into a numerical representation (embedding) using an AI model. These embeddings capture the semantic meaning of the text.
    *   **Stores:** Saves these chunks and their embeddings in the designated collection (likely using a vector database like ChromaDB).
    *   *Relevant Endpoints:* `POST /api/app/collection/add-document`, `GET /api/app/collection/documents`, `DELETE /api/app/collection/document`

3.  **Query and Generate (`Retrieval & Synthesis`):** When a user asks a question:
    *   **Retrieval:** The RAG API takes the user's query, embeds it using the same model, and searches the specified collection for text chunks with the most similar embeddings (meaning, the most semantically relevant chunks).
    *   **Augmentation:** It takes these retrieved chunks (the "context") and combines them with the original query and a prompt template you provide.
    *   **Generation:** The API sends this augmented prompt (context + query + instructions) to a specified LLM (like Mistral).
    *   **Response:** The LLM generates an answer based *both* on its general knowledge *and* the specific context provided from your documents. The RAG API then returns this final answer to your application.
    *   *Relevant Endpoint:* `POST /api/app/inferencing/retrieve_answer_using_collections` (This endpoint handles the full retrieval, augmentation, and generation process).
    *   *Inspection Endpoint:* `POST /api/app/inferencing/get_embeddings` (Useful for debugging; shows *which* chunks are retrieved for a query *before* they are sent to the LLM).

## Integrating RAG into Your Backend (FastAPI Example)

You'll typically call the RAG API from your FastAPI backend (`services.py` or `utils.py`) in response to a request from your Streamlit frontend.

**Prerequisites:**

*   `requests` library installed (`pip install requests`).
*   Have the `RAG_API_BASE_URL` (e.g., `https://hackathon-ia-et-crise.fr/admin/rag-system`) and your `API_KEY` (likely your Mistral key) available, preferably via environment variables.

```python
# Example in your backend utils.py or services.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv() # Load environment variables if using a .env file

RAG_API_BASE_URL = os.getenv("RAG_API_BASE_URL", "YOUR_RAG_API_BASE_URL") # Replace default if needed
API_KEY = os.getenv("MISTRAL_API_KEY", "YOUR_API_KEY") # Replace default if needed

# --- Helper Function to Handle RAG API Calls ---
def _call_rag_api(method: str, endpoint: str, params: dict = None, data: dict = None, files: dict = None) -> dict:
    """Generic function to call the RAG API and handle errors."""
    url = f"{RAG_API_BASE_URL}{endpoint}"
    headers = {"Accept": "application/json"} # Common header

    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == 'POST':
            # POST can have params, data (form), or files (multipart)
            response = requests.post(url, params=params, data=data, files=files, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json() # Return JSON response body

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred calling {url}: {http_err}")
        print(f"Response code: {http_err.response.status_code}, Content: {http_err.response.text}")
        raise # Re-raise the exception to be handled by the caller
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred calling {url}: {req_err}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred calling {url}: {e}")
        raise

# --- Step 1 Example: Create a Collection ---
def create_rag_collection(collection_name: str):
    """Creates a new RAG collection."""
    print(f"Attempting to create collection: {collection_name}")
    return _call_rag_api(
        method='POST',
        endpoint='/api/app/collection/new',
        params={'name': collection_name}
    )

# --- Step 2 Example: Add a Document ---
def add_document_to_collection(collection_name: str, document_path: str, embedding_model: str = "mistral-embed"):
    """Adds a document file to a specified RAG collection."""
    print(f"Attempting to add document {document_path} to collection {collection_name}")
    try:
        with open(document_path, 'rb') as f:
            files = {'document': (os.path.basename(document_path), f)}
            data = {
                'collection_name': collection_name,
                'model': embedding_model, # Ensure this model is supported/expected
                'api_key': API_KEY
                # Optional: Add 'chunk_size', 'chunk_overlap' here if needed
            }
            return _call_rag_api(
                method='POST',
                endpoint='/api/app/collection/add-document',
                files=files,
                data=data # Use 'data' for form fields alongside 'files'
            )
    except FileNotFoundError:
        print(f"Error: Document file not found at '{document_path}'")
        raise
    except Exception as e:
        print(f"Error during document preparation or API call: {e}")
        raise


# --- Step 3 Example: Query the RAG System ---
def get_rag_answer(
    query: str,
    collection_name: str,
    llm_model_name: str = "mistral-small-latest", # Or other suitable model
    prompt_template: str = "Use the following context to answer the question concisely.\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:",
    history: list = None # Expecting a list of chat messages, will be JSON serialized
):
    """Gets an answer from the RAG system using specified documents."""
    print(f"Querying collection '{collection_name}' with query: '{query}'")

    # Ensure history is a JSON string as expected by the API
    history_data_str = json.dumps(history if history is not None else [])

    params = {
        "query": query,
        "model_family": "mistral", # Adjust if using other LLM families
        "model_name": llm_model_name,
        "api_key": API_KEY,
        "prompt": prompt_template, # This tells the RAG API how to structure the final LLM call
        "collection_name": collection_name,
        "history_data": history_data_str
    }

    # This single API call handles retrieval, prompt augmentation, AND the final LLM call
    result = _call_rag_api(
        method='POST',
        endpoint='/api/app/inferencing/retrieve_answer_using_collections',
        params=params
    )
    # The result should contain the LLM's final answer, potentially along with source info
    # You might need to inspect the exact structure of 'result' (e.g., result['answer'])
    return result

# --- Example Usage (within a FastAPI route/service function) ---
# async def handle_user_query(user_input: str, team_collection: str):
#     try:
#         # 1. (Optional) Ensure collection exists or create it maybe? (Handled separately usually)
#         # 2. (Optional) Ensure documents are added? (Handled separately usually)
#
#         # 3. Get the answer using RAG
#         rag_response = get_rag_answer(
#             query=user_input,
#             collection_name=team_collection,
#             # Optionally pass history if maintaining chat context
#         )
#         print("RAG Response:", rag_response)
#         # Extract the actual answer text from the response structure
#         answer = rag_response.get("answer", "Sorry, I could not retrieve an answer.") # Adjust key based on actual response
#         return {"final_answer": answer}
#
#     except Exception as e:
#         print(f"Error handling user query with RAG: {e}")
#         # Consider raising HTTPException here for FastAPI
#         return {"error": "Failed to get RAG answer"}

```

**Explanation of the `get_rag_answer` Example:**

1.  **Inputs:** Takes the user's `query`, the target `collection_name`, the desired LLM `model_name`, a `prompt_template`, and optional chat `history`.
2.  **Prompt Template (`prompt` parameter):** This is crucial. You tell the RAG API *how* to combine the retrieved context and the original query before sending it to the LLM. The template typically includes placeholders like `{context}` and `{query}` which the RAG API will fill in. Work with organizers if a specific template format is required.
3.  **History (`history_data` parameter):** Allows you to maintain conversational context. The API expects this as a JSON string representation of the chat history (likely a list of user/assistant messages).
4.  **API Call:** It calls the single endpoint `retrieve_answer_using_collections`.
5.  **Internal API Magic:** This endpoint performs the multi-step RAG process:
    *   Searches `collection_name` for chunks relevant to `query`.
    *   Retrieves the text of those chunks (context).
    *   Formats the final prompt using your `prompt_template`, inserting the retrieved context and the user's query.
    *   Calls the specified `model_name` (using your `api_key`) with this final, augmented prompt and `history_data`.
    *   Receives the generated answer from the LLM.
6.  **Return Value:** The function returns the JSON response from the RAG API, which should contain the final LLM-generated answer, potentially along with details about the sources/chunks used (inspect the actual response to see its structure).

**Key Takeaways:**

*   The RAG API abstracts the complexity of chunking, embedding, retrieval, and LLM prompt augmentation.
*   Your primary interaction for getting answers is the `retrieve_answer_using_collections` endpoint.
*   You control the process by specifying the collection, the documents you add, the LLM model, and the final prompt template structure.
*   Integrate these helper functions into your FastAPI routes or services where you need to interact with the RAG system based on frontend actions.

Remember to manage your API keys securely and handle potential errors robustly using `try...except` blocks.
