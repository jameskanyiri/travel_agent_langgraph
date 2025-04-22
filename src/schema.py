from pydantic import BaseModel, Field

class RouteUserQuery(BaseModel):
    is_satisfactory: bool = Field(
        description="Indicates whether the user's query is clear and can be processed."
    )
    response_to_user: str = Field(
        description=(
            "Message to return to the user. "
            "If `is_satisfactory` is True, respond with a generic acknowledgment like 'Processing your request'. "
            "If False, generate a natural-sounding message. "
            "If the user's query is likely a question, respond with a clarifying question. "
            "Otherwise, provide a helpful prompt or suggestion based on the query."
        )
    )
    search_query: str = Field(
        description=(
            "A refined query used to retrieve relevant information. "
            "Populate this only if `is_satisfactory` is True; otherwise, set to null."
        )
    )


    
#Define search queries schema
class SearchQueries(BaseModel):
    queries: list[str] = Field(
        description="List of search queries.To help find relevant information",
    )
    
    
class ReflectionOutput(BaseModel):
    is_satisfactory: bool = Field(
        description="True if all required fields are well populated, False otherwise"
    )
    missing_fields: list[str] = Field(
        description="List of field names that are missing or incomplete"
    )
    search_queries: list[str] = Field(
        description="If is_satisfactory is False, provide 5 targeted search queries to find the missing information"
    )
    reasoning: str = Field(description="Brief explanation of the assessment")