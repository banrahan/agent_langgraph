from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from typing import List, Dict, Any, Optional
from .agent import Agent

class CommandLineAgent(Agent):
    """
    Command line agent.
    """

    def __init__(self, model, tools, agent_prompt, messages=None):
        """
        Initialize the command line agent.
        """

        def message_listener(event):
            """
            Custom event listener to handle events/messages from the LLM.
            """
            content =event["messages"][-1].content

            # is there anything to print?
            if content != "":
                if content.startswith("Agent >> "):
                    print(content)
                if content.startswith("{"):
                    print(content)

        def user_input_listener(event):
            """
            Custom event listener to handle user messages.
            """
            # prompt the user, possible todo is call listener instead
            human_response = input("User >> ")

            if human_response == "exit" or human_response == "quit":
                return None

            return human_response

        super().__init__(
            model,
            tools,
            agent_prompt,
            messages,
            message_listener=message_listener,
            user_input_listener=user_input_listener,
        )
