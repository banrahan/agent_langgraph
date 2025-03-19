import json
import os
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
from azure.search.documents.indexes.models import (
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()

# Get Azure Search credentials from environment variables
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
# TODO get rid of this 
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
            return json.dumps(document)
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
def update_document(id: str, updated_data: dict) -> str:
    """
    Update a document in the Azure AI Search index.
    Args:
        id: The ID of the document to update
        updated_data: A dictionary containing the updated fields and values
    Returns:
        Result message indicating success or failure
    """
    try:
        # Add the document ID to the updated data
        updated_data["id"] = id

        # Update the document in the index
        result = search_client.merge_or_upload_documents(documents=[updated_data])

        if len(result) > 0 and result[0].succeeded:
            return f"Document with ID {id} successfully updated."
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
def delete_document(id: str) -> str:
    """
    Delete a document from the Azure AI Search index.
    Args:
        doc_id: The ID of the document to delete, the id should look like a UUID and not be a word
    Returns:
        Result message indicating success or failure
    """
    try:
        # Delete the document from the index
        result = search_client.delete_documents(documents=[{"id": id}])

        if len(result) > 0 and result[0].succeeded:
            return f"Document with ID {id} successfully deleted."
        else:
            error_msg = (
                result[0].error_message
                if len(result) > 0 and hasattr(result[0], "error_message")
                else "Unknown error"
            )
            return f"Failed to delete document: {error_msg}"
    except Exception as e:
        return f"Error deleting document from search index: {str(e)}"

tool
def list_indexes() -> str:
    """
    List all indexes in the Azure AI Search resource.
    Returns:
        A JSON string containing the list of indexes
    """
    try:
        # Get Azure Search credentials from environment variables
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        
        # Validate required credentials
        if not all([search_endpoint, search_key]):
            return json.dumps(
                {
                    "error": "Azure Search credentials not configured. Please set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY environment variables."
                }
            )
            
        # Initialize the search client
        credential = AzureKeyCredential(search_key)
        search_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        
        # List indexes
        indexes = search_client.list_indexes()
        index_names = [index.name for index in indexes]
        
        return json.dumps(index_names)
    except Exception as e:
        print(e)
        return json.dumps({"error": f"Error listing indexes: {str(e)}"})


@tool
def create_index(index_name: str, fields: list) -> str:
    """ 
    Create an Azure Search index with the given name and fields.
    Args:
        index_name: The name of the index to create.
        fields: List of dictionaries, where each dictionary contains 'name' (field name) and 'type' (field type). 
               Example: [{"name": "id", "type": "Edm.String", "key": True}, 
                        {"name": "title", "type": "Edm.String", "searchable": True}]
        
    Returns:
        A message indicating success or failure.
    """
    try:
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        
        # Map string type names to SearchFieldDataType enum values
        type_mapping = {
            "Edm.String": SearchFieldDataType.String,
            "Edm.Int32": SearchFieldDataType.Int32,
            "Edm.Int64": SearchFieldDataType.Int64,
            "Edm.Double": SearchFieldDataType.Double,
            "Edm.Boolean": SearchFieldDataType.Boolean,
            "Edm.DateTimeOffset": SearchFieldDataType.DateTimeOffset,
            "Edm.GeographyPoint": SearchFieldDataType.GeographyPoint,
            "Collection(Edm.String)": SearchFieldDataType.Collection(SearchFieldDataType.String)
        }
        
        # Create the list of SimpleField objects from the input fields
        index_fields = []
        for field in fields:
            field_name = field.get("name")
            field_type_str = field.get("type")
            
            if not field_name or not field_type_str:
                return f"Error: Each field must have a 'name' and 'type' property"
                
            # Get the corresponding enum value or default to String if not found
            field_type = type_mapping.get(field_type_str, SearchFieldDataType.String)
            
            # Extract other field properties with defaults
            is_key = field.get("key", False)
            is_searchable = field.get("searchable", True)
            is_filterable = field.get("filterable", not is_key)
            is_sortable = field.get("sortable", not is_key)
            is_facetable = field.get("facetable", not is_key)
            is_retrievable = field.get("retrievable", True)
            
            # Create the field
            index_fields.append(
                SimpleField(
                    name=field_name,
                    type=field_type,
                    key=is_key,
                    searchable=is_searchable,
                    filterable=is_filterable,
                    sortable=is_sortable,
                    facetable=is_facetable,
                    retrievable=is_retrievable
                )
            )
        
        # Ensure at least one field is marked as a key
        if not any(field.key for field in index_fields):
            return "Error: At least one field must be marked as a key field"
            
        # Create the SearchIndex object
        index = SearchIndex(name=index_name, fields=index_fields)
        
        # Create the index using the SearchIndex object
        index_client.create_index(index=index)
        
        return f"Index '{index_name}' created successfully with {len(fields)} fields."
    except Exception as e:
        return f"Error creating index: {str(e)}"


@tool
def delete_index(index_name: str) -> str:
    """
    Delete an Azure Search index with the given name.
    Args:
        index_name: The name of the index to delete.
    Returns:
        A message indicating success or failure.
    """
    try:
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        index_client.delete_index(index=index_name)
        return f"Index '{index_name}' deleted successfully."
    except Exception as e:
        return f"Error deleting index: {str(e)}"

@tool
def describe_index_schema(index_name: str) -> str:
    """
    Get the schema definition of an Azure AI Search index, showing all fields and their properties.
    Args:
        index_name: The name of the index to describe
    Returns:
        JSON string containing the index schema information
    """
    try:
        # Get Azure Search credentials from environment variables
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        
        # Validate required credentials
        if not all([search_endpoint, search_key]):
            return json.dumps({
                "error": "Azure Search credentials not configured. Please set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY environment variables."
            })
            
        # Initialize the search client
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        
        # Get the index definition
        try:
            index = index_client.get_index(name=index_name)
        except Exception as e:
            return json.dumps({"error": f"Index '{index_name}' not found: {str(e)}"})
        
        # Create a schema description with field information
        schema_info = {
            "name": index.name,
            "fields": []
        }
        
        # Add field definitions
        for field in index.fields:
            field_info = {
                "name": field.name,
                "type": str(field.type),
                "key": field.key,
                "searchable": getattr(field, "searchable", False),
                "filterable": getattr(field, "filterable", False),
                "sortable": getattr(field, "sortable", False),
                "facetable": getattr(field, "facetable", False),
                "retrievable": getattr(field, "retrievable", True)
            }
            schema_info["fields"].append(field_info)
        
        # Add other index properties if they exist
        if hasattr(index, "scoring_profiles") and index.scoring_profiles:
            schema_info["scoring_profiles"] = [profile.name for profile in index.scoring_profiles]
        
        if hasattr(index, "analyzers") and index.analyzers:
            schema_info["analyzers"] = [analyzer.name for analyzer in index.analyzers]
            
        return json.dumps(schema_info, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error retrieving index schema: {str(e)}"})
