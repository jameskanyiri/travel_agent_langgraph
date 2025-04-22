from dataclasses import dataclass, field
from typing import Any, Optional, Annotated, List
import operator
from langgraph.graph.message import add_messages, BaseMessage





@dataclass(kw_only=True)
class InputState:
    """Input state defines the interface between the graph and the user (external API)."""
    
    messages: Annotated[list[BaseMessage], add_messages]
    "A list of messages exchanged during the agent's conversation"


@dataclass(kw_only=True)
class AgentState:
    """Input state defines the interface between the graph and the user (external API)."""
    
    messages: Annotated[list[BaseMessage], add_messages]
    "A list of messages exchanged during the agent's conversation"

    user_query: str = field(default=None)
    "query provided by the user."


    search_queries: list[str] = field(default=None)
    "List of generated search queries to find relevant information"

    search_results: list[dict] = field(default=None)
    "List of search results"

    completed_notes: Annotated[list, operator.add] = field(default_factory=list)
    "Notes from completed research related to the schema"

    info: dict[str, Any] = field(default=None)
    """
    A dictionary containing the extracted and processed information
    based on the user's query and the graph's execution.
    This is the primary output of the enrichment process.
    """

    is_satisfactory: bool = field(default=None)
    "True if all required fields are well populated, False otherwise"

    reflection_steps_taken: int = field(default=0)
    "Number of times the reflection node has been executed"
    
    output: str = field(default=0)
    "The final research output"


@dataclass(kw_only=True)
class OutputState:
    """The response object for the end user.

    This class defines the structure of the output that will be provided
    to the user after the graph's execution is complete.
    """

    output: str = field(default=0)
    "The final research output"

    search_results: list[dict] = field(default=None)
    "List of search results"