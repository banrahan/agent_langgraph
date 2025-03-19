import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from agents.workflow_agent import WorkflowAgent
from tools.ai_search_tools import search

# Load environment variables from .env file
load_dotenv()

# Initialize the AzureChatOpenAI model
model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0,
)


def workflow_agent_example():
    """
    Example showing how to use WorkflowAgent with event listeners.
    """
    # Agent prompt
    search_agent_prompt = """
You are an expert database administrator and data engineer specializing in Azure AI Search.
Your goal is to search a database with the tool **search** and return the results in a JSON object. Do not add anything else to the JSON object.

Instructions:
1. Use the **search** tool to find documents matching the user's query, found in the user's json input as **query**.
2. Return the results in a JSON object.
3. Once you are done return **TERMINATE** to indicate that you are done.
    """

    # Initialize the workflow agent
    search_agent = WorkflowAgent(
        model=model,
        tools=[
            search,
        ],
        agent_prompt=search_agent_prompt,
    )

    result = search_agent.run_workflow(
        {"query": "Search for documents containing 'azure'"}
    )
    print(result)


def main():
    """
    Main function to run the agent.
    """

    workflow_agent_example()


if __name__ == "__main__":
    main()
