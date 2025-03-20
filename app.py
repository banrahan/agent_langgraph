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
from tools.html_tools import (
    html_template,
    javascript_list_to_html,
    button,
    search_bar,
)
from agents.html_agent import (
    HTMLAgent,
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




@app.route("/ui/<path:path>", methods=["GET"])
def user_interface(path):
    """User interface for the application"""

    ui_agent_prompt = f"""
You are an amazing web developer that loves to use bootstrap. Your job is to create a front end for a create page. The create page is for a database of document.  Use bootstrap for styling, html, and vanilla javascript as much as possible. What you return should be a complete html page that can be rendered in a browser. Do not add any additional text or explanation.

STEP 1: IDENTIFY THE OPERATION TYPE
Use the path to identify the user intent. The current URL path is: ```{path}```

First check if this is a standard operation:
- If path equals "search" or contains words like "find", "get", "query": This is a SEARCH operation and you should create a SEARCH PAGE

SEARCH PAGE:
For a search page, create a search bar that allows the user to enter their search query. The search bar should be styled using bootstrap and should have a submit button. The search bar should be able to handle the search query and return the results.


TOOLS:
- **html_template**: This tool allows you to create a complete HTML template for the user interface. Use this tool to create a complete HTML template for the search page.
- **button**: This tool allows you to create a button for the user interface. Use this tool to create a button that can be used to submit the search query.
- **search_bar**: This tool allows you to create a search bar for the user interface. Use this tool to create a search bar for the user to enter their search query.
- **javascript_list_to_html**: This tool creates a javascript function that you can called in the user interface. The generated function should be able to take a list of items and create a html list. Use this tool to create a javascript function that can take the search results and display them in a list format.
BUTTON DETAILS:
For all of the different operations on the page, attach the correct API endpoint via javascript. Use post for everthing, and put the parameters in a json object.
- If the button is for a search operation, use the something like 127.0.0.1:5000/api/search endpoint
- If the button is for a delete operation, use the something like 127.0.0.1:5000/api/delete endpoint
- If the button is for a create operation, use the something like 127.0.0.1:5000/api/create endpoint
- If the button is for a update operation, use the something like 127.0.0.1:5000/api/update endpoint


IMPORTANT: Feel free to use the tools in any order you see fit, but ensure that you only execute one tool at a time. If multiple tools are needed, run them sequentially and return the final result. Feel free to generate any additional HTML, CSS, or JavaScript code needed to create a complete web page.
"""
    # Initialize the workflow agent with a higher recursion limit
    api_agent = HTMLAgent(
        model=model,
        tools=[
            html_template,
            button,
            search_bar,
            javascript_list_to_html,
        ],
        agent_prompt=ui_agent_prompt,
    )

    # Pass path directly rather than as action to make it clearer
    result = api_agent.render_html({})

    return result

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)



# - If path equals "delete" or contains words like "remove", "delete", "trash": This is a DELETE operation and should return a delete page
# - If path equals "update" or contains words like "change", "modify", "update": This is an UPDATE operation and should return an update form