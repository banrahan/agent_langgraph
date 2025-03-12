import uuid

from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command


class Agent:
    """
    The agent class.
    """

    def __init__(
        self,
        model,
        tools,
        agent_prompt,
        messages=None,
        message_listener=None,
        user_input_listener=None,
    ):
        """
        Initialize the agent with a model, tools, and an optional system prompt.
        Args:
            model: The model to use.
            tools: The tools to use.
            system_prompt: The system prompt to use.
            messages: The initial messages to use. (optional)
            message_listener: Optional event listener to handle messages from the llm.
            user_input_listener: Optional event listener to handle user input.
        """
        self.model = model
        self.tools = tools
        self.system_prompt = agent_prompt
        self.message_listener = message_listener
        self.user_input_listener = user_input_listener

        self.thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
        self.state = {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            ]
        }
        if messages:
            self.state["messages"].extend(messages)

        graph = StateGraph(MessagesState)
        graph.add_node("agent", self.call_model)
        graph.add_node("tools", ToolNode(tools=tools))
        graph.add_edge("agent", "tools")
        graph.add_edge("tools", "agent")

        graph.set_entry_point("agent")

        self.graph = graph.compile(checkpointer=MemorySaver())
        self.model = model.bind_tools(tools, tool_choice="auto")

    def run(self, command=None):
        """
        Run the agent.
        """
        if command is None:
            for event in self.graph.stream(
                self.state, config=self.thread_config, stream_mode="values"
            ):
                self.handle_event(event)
        else:
            for event in self.graph.stream(
                command, config=self.thread_config, stream_mode="values"
            ):
                self.handle_event(event)

        # check that we in fact do have an interrupt
        if self.has_interrupt() > 0:
            human_response = None
            if (
                hasattr(self, "user_input_listener")
                and self.user_input_listener is not None
            ):
                # call the user input listener
                human_response = self.user_input_listener(event)
            else:
                raise NotImplementedError("User input listener is not implemented.")

            if human_response is not None:
                command = Command(resume=human_response)
                return self.run(command=command)
            else:
                # if the user input listener returns None, we stop the agent
                return

    def handle_event(self, event) -> None:
        """
        Handle an event.
        """
        message = event["messages"][-1]
        if hasattr(self, "message_listener") and self.message_listener is not None:
            return self.message_listener(event)
        else:
            raise NotImplementedError("Message listener is not implemented.")

    def call_model(self, state: MessagesState):
        """
        Call the model with the current state.
        """
        messages = state["messages"]
        messages = self.model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [messages]}

    def has_interrupt(self) -> bool:
        """
        Check if there is an interrupt.
        """
        return len(self.graph.get_state(self.thread_config).tasks) > 0


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
