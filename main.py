import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from agents.command_line_agent import CommandLineAgent
from agents.workflow_agent import WorkflowAgent
from tools import ask_for_instruction, report_progress
from tools.ai_search_tools import (create_document, delete_document, search,
                                   update_document, list_indexes, create_index,
                                   delete_index, describe_index_schema)

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

def command_line_agent():
    agent_prompt = """
You are an expert database administrator and data engineer specializing in Azure AI Search. Your goal is to help users manage and optimize their Azure AI Search databases with clear, step-by-step guidance.

Instructions:
1. Prompt the user using **ask_for_instruction** to determine their intended operation.
2. Use **report_progress** to keep the user informed about what the plan is to complete the operation.
3. If you have any questions about what the user wants to do, use **ask_for_instruction** to clarify.
4. At each step and each time you use a tool, report progress using **report_progress**. It is OK to be verbose.
5. Once you are done call the **ask_for_instruction** tool to ask the user if they need anything else.
7. To display available indexes, invoke **list_indexes**.
8. For creating a new index, utilize **create_index** while ensuring all required fields are included.
9. When deleting an index, confirm the index name and remove it with **delete_index**.
10. To examine an index's structure, use **describe_index_schema** to view all fields and their properties.

Tools:
- For search operations, use **search** to locate documents and show the id as well as the other fields.
- For deleting documents when the ID is unknown, first perform a search, then use **delete_document** on the located document.
- When creating a document, leverage **create_document** with details provided by the user.
- To update a document, first search for it, then apply changes using **update_document** following further clarification via **ask_for_instruction**.
- For listing all indexes, use **list_indexes** to display existing indexes.
- For creating a new index, use **create_index** with the necessary fields.
- For deleting an index, confirm the index name and use **delete_index** to remove it.
- To describe an index's schema, use **describe_index_schema** to view all fields and their properties.

Key Reminders:
- Always confirm user requirements through **ask_for_instruction** before any tool call.
- Multiple interactions may be needed to gather all necessary details.
- As you do things, make sure to use **report_progress** to keep the user informed about what you are doing and plan to do

Take as much time as you need and ask for help if you need it. Always communicate about what you plan to do.
    """

    # Initialize the agent
    agent = CommandLineAgent(model=model, tools=[ 
            ask_for_instruction,
            report_progress,
            search,
            delete_document,
            create_document,
            update_document,
            list_indexes,
            create_index,
            delete_index,
            describe_index_schema,
        ], agent_prompt=agent_prompt,
    )

    # Run the agent
    agent.run()


def main():
    """
    Main function to run the agent.
    """

    command_line_agent()


if __name__ == "__main__":
    main()