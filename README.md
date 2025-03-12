# AI Agent (using langgraph)

This project implements an AI search agent that helps with information retrieval and processing, it also has some classes that make agents easier. It is a work in progress and the agents are continually being improved.

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

If you prefer to use a virtual environment (recommended):

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

1. Create a `.env` file in the project root directory:

```bash
touch .env
```

2. Add the following environment variables to the `.env` file:

```
# OpenAI API credentials
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=your_api_version_here

# Azure Search credentials (if using Azure Search)
AZURE_SEARCH_SERVICE_ENDPOINT=your_azure_search_endpoint_here
AZURE_SEARCH_INDEX_NAME=your_azure_search_index_name
AZURE_SEARCH_API_KEY=your_azure_search_api_key
```

Make sure to replace the placeholder values with your actual API keys and configuration settings.

## Usage Example

Here's an example of how to import and the Agent class to do a chat:

```python
from agents import CommandLineAgent
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from tools import ask_for_instruction, report_progress

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

# what do you want the agent to do
agent_prompt = """
You are a helpful assistant that can provide information.
"""

# Initialize the agent with the model, whatever tools, and the agent prompt 
agent = CommandLineAgent(model=model, tools=[
    ask_for_instruction,
    report_progress
], agent_prompt=agent_prompt)

# Run the agent
agent.run()
```