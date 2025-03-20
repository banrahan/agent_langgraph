from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from agents.workflow_agent import WorkflowAgent
from tools.ai_search_tools import (
    search,
    delete_document,
    update_document,
    create_document,
)
from agents.html_renderers import (
    render_search_page,
    render_create_page,
)

# Create Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load environment variables from .env file
load_dotenv()

# Initialize the model
model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0,
)

@app.route("/api/<path:path>", methods=["GET", "POST"])
def api(path):
    """API endpoint for various operations"""
    data = request.json

    api_agent_prompt = f"""
You are a REST API implementation service. Follow these instructions precisely.

STEP 1: IDENTIFY THE OPERATION TYPE
The current API path is: ```{path}```
The request data is: ```{data}```
The request method is: ```{request.method}```

First check if this is a standard operation:
- If path equals "search" or contains words like "find", "get", "query": This is a SEARCH operation
- If path equals "delete" or contains words like "remove", "delete", "trash": This is a DELETE operation
- If path equals "create" or contains words like "add", "new", "create": This is a CREATE operation
- If path equals "update" or contains words like "change", "modify", "update": This is an UPDATE operation

For unanticipated URLs:
- Analyze the path's intent and the provided data structure
- Use your best judgment to determine what set of operations are needed to fulfill the request
- Consider URL structure, HTTP method, and data payload when determining intent
- If the path seems like a custom endpoint (e.g., "/api/documents/latest", "/api/filter-by-category"), interpret what the user is trying to accomplish

STEP 2: EXECUTE THE CORRECT TOOL
Based on the operation identified, execute EXACTLY ONE of these tools:

For SEARCH operations:
- Use the **search** tool with "query" parameter from the data
- Example: search(query=data.get("query", ""))

For DELETE operations:
- EXTREMELY IMPORTANT: Use the **delete_document** tool with EXACTLY the "id" value from the data object
- DO NOT modify, generate, or interpret the ID - use it exactly as provided
- CORRECT: delete_document(id=data["id"])
- INCORRECT: delete_document(id="some_generated_id")
- INCORRECT: delete_document(id=data.get("document_id"))

For CREATE operations:
- Use the **create_document** tool with the document data
- Example: create_document(document=data)

For UPDATE operations:
- Use the **update_document** tool with the document data
- Example: update_document(document=data)

STEP 3: RETURN RESULTS
Return ONLY the JSON result from the tool without any additional text or explanation.

IMPORTANT: Feel free to use the tools in any order you see fit, but ensure that you only execute one tool at a time. If multiple tools are needed, run them sequentially and return the final result.
"""

    # Initialize the workflow agent with a higher recursion limit
    api_agent = WorkflowAgent(
        model=model,
        tools=[
            search,
            delete_document,
            update_document,
            create_document,
        ],
        agent_prompt=api_agent_prompt,
    )

    # Pass path directly rather than as action to make it clearer
    result = api_agent.run_workflow({})

    return jsonify(result)

# @app.route("/api/search", methods=["POST"])
# def api_search():
#     """API endpoint for search operations"""
#     data = request.json

#     search_agent_prompt = """
# You are an expert database administrator and data engineer specializing in Azure AI Search.
# Your goal is to search a database with the tool **search** and return the results in a JSON object. Do not add anything else to the JSON object.

# Instructions:
# 1. Use the **search** tool to find documents matching the user's query, found in the user's json input as **query**.
# 2. Return the results in a JSON object.
# """

#     # Initialize the workflow agent
#     search_agent = WorkflowAgent(
#         model=model,
#         tools=[
#             # NOTE: If I want to change the service that I am using, I can just change the tool here..not much code change, just this and the prompt
#             search,
#         ],
#         agent_prompt=search_agent_prompt,
#     )

#     result = search_agent.run_workflow({"query": data.get("query", "")})

#     # Return the result as JSON
#     return jsonify(result)

@app.route("/ui/<path:path>", methods=["GET"])
def user_interface(path):
    """User interface for the application"""

    ui_agent_prompt = f"""
You are a web server that returns web pages based on the URL path and the tools available. The application is front end to a REST API that allows users to search, create, update, and delete documents in a database. Use bootstrap for styling, html, and vanilla javascript as much as possible. What you return should be a complete html page that can be rendered in a browser. Do not add any additional text or explanation.

STEP 1: IDENTIFY THE USER INTENT
use the path to identify the user intent. The current URL path is: ```{path}```

First check if this is a standard operation:
- If path equals "search" or contains words like "find", "get", "query": user **render_search_page** tool to render a search page
- If path equals "create" or contains words like "add", "new", "create": user **render_create_page** tool to render a create page
"""
    # Initialize the workflow agent with a higher recursion limit
    api_agent = WorkflowAgent(
        model=model,
        tools=[
            render_search_page,
            render_create_page,
        ],
        agent_prompt=ui_agent_prompt,
    )

    # Pass path directly rather than as action to make it clearer
    result = api_agent.run_workflow({})

    return result["page"]

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)



# - If path equals "delete" or contains words like "remove", "delete", "trash": This is a DELETE operation and should return a delete page
# - If path equals "update" or contains words like "change", "modify", "update": This is an UPDATE operation and should return an update form