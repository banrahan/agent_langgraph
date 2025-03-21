import json

from .agent import Agent


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
        Run the workflow agent, tries to return a dictionary from JSON.
        """
        # Add the data to the messages
        self.state['messages'].extend({"role": "user", "content": json.dumps(data)})

        for event in self.graph.stream(
            self.state, config=self.thread_config, stream_mode="values"
        ):
            print(event)
            
            try:
                content = event["messages"][-1].content

                content = json.loads(event["messages"][-1].content)

                if content != "" and content != "content":
                    return content

            except Exception as e:
                pass

        return None