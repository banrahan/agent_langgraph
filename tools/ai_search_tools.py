import json
import os
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import SearchFieldDataType
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.types import interrupt

# Load environment variables from .env file
load_dotenv()

# Get Azure Search credentials from environment variables
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")

# Initialize the search client
credential = AzureKeyCredential(search_key)
search_client = SearchClient(
    endpoint=search_endpoint, index_name=index_name, credential=credential
)


@tool
def create_document(title: str, content: str) -> str:
    """
    Add a document to the Azure AI Search index.
    Args:
        title: The title of the document
        content: The main content of the document
    Returns:
        Result message indicating success or failure
    """
    try:
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())

        # Create document object
        document = {
            "id": doc_id,
            "title": title,
            "content": content,
        }

        # Upload the document to the index
        result = search_client.upload_documents(documents=[document])

        # Check if upload was successful
        if len(result) > 0 and result[0].succeeded:
            return f"Document successfully added to index with ID: {doc_id}"
        else:
            error_msg = (
                result[0].error_message
                if len(result) > 0 and hasattr(result[0], "error_message")
                else "Unknown error"
            )
            return f"Failed to add document: {error_msg}"
    except Exception as e:
        return f"Error adding document to search index: {str(e)}"


@tool
def search(query: str) -> str:
    """
    Search for information using Azure AI Search.
    Args:
        query: The search query string
    Returns:
        Search results as a JSON object with fields 'id', 'title', and 'content'
    """
    try:
        # Execute search query
        results = search_client.search(
            search_text=query,
            top=5,  # Return top 5 results
            search_fields=["content", "title"],  # Adjust based on your index schema
            select=["id", "content", "title"],  # Adjust based on your index schema
        )

        # Format search results
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.get("id", "No ID"),
                "title": result.get("title", "No Title"),
                "content": result.get("content", "No Content"),
            }
            formatted_results.append(formatted_result)

        if formatted_results:
            return json.dumps(formatted_results)
        else:
            return json.dumps({"message": "No results found for your query."})
    except Exception as e:
        return json.dumps({"error": f"Error performing search: {str(e)}"})


@tool
def update_document(doc_id: str, updated_data: dict) -> str:
    """
    Update a document in the Azure AI Search index.
    Args:
        doc_id: The ID of the document to update
        updated_data: A dictionary containing the updated fields and values
    Returns:
        Result message indicating success or failure
    """
    try:
        # Add the document ID to the updated data
        updated_data["id"] = doc_id

        # Update the document in the index
        result = search_client.merge_or_upload_documents(documents=[updated_data])

        if len(result) > 0 and result[0].succeeded:
            return f"Document with ID {doc_id} successfully updated."
        else:
            error_msg = (
                result[0].error_message
                if len(result) > 0 and hasattr(result[0], "error_message")
                else "Unknown error"
            )
            return f"Failed to update document: {error_msg}"
    except Exception as e:
        return f"Error updating document in search index: {str(e)}"


@tool
def delete_document(doc_id: str) -> str:
    """
    Delete a document from the Azure AI Search index.
    Args:
        doc_id: The ID of the document to delete
    Returns:
        Result message indicating success or failure
    """
    try:
        # Delete the document from the index
        result = search_client.delete_documents(documents=[{"id": doc_id}])

        if len(result) > 0 and result[0].succeeded:
            return f"Document with ID {doc_id} successfully deleted."
        else:
            error_msg = (
                result[0].error_message
                if len(result) > 0 and hasattr(result[0], "error_message")
                else "Unknown error"
            )
            return f"Failed to delete document: {error_msg}"
    except Exception as e:
        return f"Error deleting document from search index: {str(e)}"