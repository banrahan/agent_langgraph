from langchain_core.tools import tool
from langgraph.types import interrupt


@tool
def ask_for_instruction() -> str:
    """
    Ask the user for an instruction
    """
    return interrupt("User >> ")


@tool
def report_progress(str):
    """
    Report progress to the user
    Args:
        str: The progress message
    """
    return f"Agent >> {str}"

