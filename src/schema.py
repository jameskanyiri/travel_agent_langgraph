from pydantic import BaseModel, Field


class RouteUserQuery(BaseModel):
    is_satisfactory: bool = Field(
        description="True if all the user query is clear"
    )
    response_to_user: str = Field(
        description="If is_satisfactory is true return `Processing your request` else respond with a user query"
    )
    search_query: str = Field(
        description="Query to help find relevant information. Populate this field id is_satisfactory is True else Null"
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