from dataclasses import dataclass, field
from typing import Any, Optional, Annotated, List
import operator
from langgraph.graph.message import add_messages, BaseMessage



TRAVEL_DOCUMENT_SCHEMA = {
    "title": "TravelDocumentationRequirements",
    "description": "Details about the travel requirements between an origin and destination country.",
    "type": "object",
    "properties": {
        "origin_country": {
            "type": "string",
            "description": "The country the user is traveling from"
        },
        "destination_country": {
            "type": "string",
            "description": "The country the user is traveling to"
        },
        "visa_requirements": {
            "type": "string",
            "description": "Detailed visa requirements including type, process, and duration"
        },
        "passport_requirements": {
            "type": "string",
            "description": "Information about passport validity, blank pages, and expiration policies"
        },
        "additional_documents": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Other documents needed such as return ticket, vaccination records, travel insurance, etc."
        },
        "travel_advisories": {
            "type": "string",
            "description": "Any current travel advisories, restrictions, or health notices related to the destination"
        }
    },
    "required": [
        "origin_country",
        "destination_country",
        "visa_requirements",
        "passport_requirements",
        "additional_documents",
        "travel_advisories"
    ]
}



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

    extraction_schema: dict[str, Any] = field(
        default_factory=lambda: TRAVEL_DOCUMENT_SCHEMA
    )
    "The json schema defines the information the agent is tasked with filling out."


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