from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from typing import List, Dict, Any, Optional
from .agent import Agent
import json

class WorkflowAgent(Agent):
    """
    Workflow agent.
    """

    def __init__(self, model, tools, agent_prompt, messages=None):
        super().__init__(
            model,
            tools,
            agent_prompt,
            messages,
        )

    def run_workflow(self, data):
        """
        Run the workflow agent.
        """
        # Add the data to the messages
        self.state['messages'].extend({"role": "user", "content": json.dumps(data)})

        for event in self.graph.stream(
            self.state, config=self.thread_config, stream_mode="values"
        ):
            # print(event)
            
            try:
                content = event["messages"][-1].content
                # this means it is probably html
                if content.startswith("<"):
                    return content

                content = json.loads(event["messages"][-1].content)

                if content != "" and content != "content":
                    return content

            except Exception as e:
                pass

        return None