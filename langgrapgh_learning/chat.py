from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model


# Load environment variables (.env)
load_dotenv()

# Initialize OpenAI chat model
llm = init_chat_model(model="gpt-4.1-mini", model_provider="openai")


# ---------------------------
# Define Graph State
# ---------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ---------------------------
# Chatbot Node
# ---------------------------
def chatbot(state: State):
    # Directly pass messages to chat model
    response = llm.invoke(state["messages"])

    # Append AI response
    return {"messages": [response]}


# ---------------------------
# Sample Node
# ---------------------------
def samplenode(state: State):
    return {"messages": ["Sample message appended"]}


# ---------------------------
# Build Graph
# ---------------------------
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()


# ---------------------------
# Run Graph
# ---------------------------
initial_state = {"messages": ["Hi, my name is Ahmad"]}

updated_state = graph.invoke(initial_state)

print("\nUpdated State:\n")
print(updated_state)
