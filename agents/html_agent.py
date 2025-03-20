import json
import os
from flask import jsonify

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

from .agent import Agent
from .workflow_agent import WorkflowAgent


class HTMLAgent(Agent):
    """
    This class is responsible for rendering HTML pages using the Azure OpenAI model.
    """

    def __init__(self, model, tools, agent_prompt, messages=None):
        super().__init__(
            model,
            tools,
            agent_prompt,
            messages,
        )

    def is_html_page(self, input_string):
        """
        Check if the input string is a valid HTML page.
        """
        soup = BeautifulSoup(input_string, "html.parser")
        return bool(soup.find("html") and soup.find("body"))  # Returns True if the string contains <html> and <body> tags

    def render_html(self, data):
        """
        Run the HTML agent, tries to return an HTML page
        """
        # Add the data to the messages
        self.state["messages"].extend({"role": "user", "content": json.dumps(data)})

        for event in self.graph.stream(
            self.state, config=self.thread_config, stream_mode="values"
        ):
            try:
                content = event["messages"][-1].content

                if self.is_html_page(content):
                    return content

            except Exception as e:
                pass

        return None


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


@tool
def render_search_page() -> str:
    """Renders the search page, returns HTML."""

    render_search_prompt = """
You are an amazing web developer that loves to use bootstrap. Your job is to create a front end for a search page. The search page is for a database of document.  Use bootstrap for styling, html, and vanilla javascript as much as possible. What you return should be a complete html page that can be rendered in a browser. Do not add any additional text or explanation.

The search page should include the following:
- A Navigation bar with links to the different operations (search, create, update, delete) the urls should have  
-- The search navigation link should be http://127.0.0.1:5000/ui/search
-- The create navigation link should be http://127.0.0.1:5000/ui/create
-- The delete navigation link should be http://127.0.0.1:5000/ui/delete
-- The update navigation link should be http://127.0.0.1:5000/ui/update
- A title that describes the operation
- A form for the operation
- A button to submit the form

For all of the different operations on the page, use the correct API endpoint, use post for everthing, and put the parameters in a json object
- If the button is for a search operation, use the something like 127.0.0.1:5000/api/search endpoint
- If the button is for a delete operation, use the something like 127.0.0.1:5000/api/delete endpoint
- If the button is for a create operation, use the something like 127.0.0.1:5000/api/create endpoint
- If the button is for a update operation, use the something like 127.0.0.1:5000/api/update endpoint

IMPORTANT:
- Create a helper function in javascript that will take the json object and convert it to a html table. Include this function in the html page and call it whenever you are rendering the results of a request. 
- Each row should have a button to delete the document, and a button to update the document. The update button should take the user to a new page with a form to update the document.
- Try your best to respond quickly, the user is waiting for you.
"""
    # Check if the templates directory exists, if not create it
    if not os.path.exists("templates"):
        os.makedirs("templates")

    result = ""
    # Check if the search.html file exists, if not call the renderer
    if not os.path.exists("templates/search.html"):

        renderer = HTMLAgent(
            model=model,
            tools=[],
            agent_prompt=render_search_prompt,
        )

        result = renderer.render_html({})

        # save the result to a file in the templates directory
        with open("templates/search.html", "w") as f:
            f.write(result)
    else:
        # read the file and return it
        with open("templates/search.html", "r") as f:
            result = f.read()

    return {'page': result}


@tool
def render_create_page() -> str:
    """Renders the create page, returns HTML."""

    render_create_prompt = """
You are an amazing web developer that loves to use bootstrap. Your job is to create a front end for a create page. The create page is for a database of document.  Use bootstrap for styling, html, and vanilla javascript as much as possible. What you return should be a complete html page that can be rendered in a browser. Do not add any additional text or explanation.

The schema for the document is as follows:
{
    "title": "string",
    "content": "string",
}

The create page should include the following:
- A Navigation bar with links to the different operations (search, create, update, delete) the urls should have
-- The search navigation link should be http://127.0.0.1:5000/ui/search
-- The create navigation link should be http://127.0.0.1:5000/ui/create
-- The delete navigation link should be http://127.0.0.1:5000/ui/delete
-- The update navigation link should be http://127.0.0.1:5000/ui/update
- A title that describes the operation
- A form for the operation
- A button to submit the form

For all of the different operations on the page, use the correct API endpoint, use post for everthing, and put the parameters in a json object
- If the button is for a search operation, use the something like 127.0.0.1:5000/api/search endpoint
- If the button is for a delete operation, use the something like 127.0.0.1:5000/api/delete endpoint
- If the button is for a create operation, use the something like 127.0.0.1:5000/api/create endpoint
- If the button is for a update operation, use the something like 127.0.0.1:5000/api/update endpoint

IMPORTANT:
- Create a helper function in javascript that will take the json object and convert it to a html table. Include this function in the html page and call it whenever you are rendering the results of a request. 
- Each row should have a button to delete the document, and a button to update the document. The update button should take the user to a new page with a form to update the document.
"""

    renderer = WorkflowAgent(
        model=model,
        tools=[],
        agent_prompt=render_create_prompt,
    )

    return renderer.run_workflow({})
