import asyncio
import json
from langgraph.graph import StateGraph, END
from src.state import AgentState, InputState, OutputState
from langgraph.types import Command
from typing import Literal
from src.utils import (
    get_current_date,
    deduplicate_sources,
    format_sources,
    format_all_notes,
)
from src.prompts import (
    QUERY_WRITER_PROMPT,
    SUMMARIZE_INSTRUCTIONS,
    EXTRACTION_PROMPT,
    REFLECTION_INSTRUCTIONS,
    AGENT_PROMPT,
    FORMAT_RESPONSE_PROMPT
)
from src.schema import SearchQueries, ReflectionOutput, RouteUserQuery
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

from tavily import AsyncTavilyClient


from langchain_openai import AzureChatOpenAI

# Initialize llm
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1-mini",
    api_version="2024-12-01-preview",
    temperature=0,
)

tavily_async_client = AsyncTavilyClient()


async def agent(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["generate_queries", END]]:
    """Langgraph node to understand user intent"""

    # get messages from state
    messages = state.messages

    # get Configuration
    configuration = Configuration.from_runnable_config(config)
    user_name = configuration.user_name
    assistant_name = configuration.assistant_name
    assistant_role = configuration.assistant_role

    system_instruction = AGENT_PROMPT.format(
        conversation_history=messages,
        user_name=user_name,
        assistant_role=assistant_role,
        assistant_name=assistant_name,
    )

    structured_llm = llm.with_structured_output(RouteUserQuery)

    response = await structured_llm.ainvoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(content=f"Please help analyse the user intent"),
        ]
    )

    if response.is_satisfactory:
        return Command(
            update={
                "user_query": response.search_query,
                "messages": AIMessage(content=response.response_to_user),
            },
            goto="generate_queries",
        )
    else:
        return Command(
            update={
                "messages": AIMessage(content=response.response_to_user),
            },
            goto=END,
        )


async def generate_queries(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["web_research"]]:
    """
    Langgraph node that generates a search queries based on the user query

    Uses a structured LLM to generate  optimized search queries for web research based on the user query.

    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable

    Returns:
        Command: To help update the graph state AND route to the next node

    """

    # get user query
    user_query = state.user_query

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    max_search_queries = configurable.max_search_queries
    assistant_role = configurable.assistant_role

    # get the current date
    current_date = get_current_date()

    # Format the system instructions
    system_instruction = QUERY_WRITER_PROMPT.format(
        user_query=user_query,
        max_search_queries=max_search_queries,
        assistant_role=assistant_role,
        current_date=current_date,
    )

    # Bind the schema to rhe model
    structured_llm = llm.with_structured_output(SearchQueries)

    # Invoke the model to produce structured output that matches the schema
    response = await structured_llm.ainvoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(
                content="Please generate a list of search queries to help gather relevant information"
            ),
        ]
    )

    # Queries
    query_list = [query for query in response.queries]

    # Perform state update and go the web search mode
    return Command(
        # state update
        update={"search_queries": query_list},
        # Control flow
        goto="web_research",
    )


async def web_research(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["extract_info"]]:
    """Langgraph node to  multi step web research using the generated search queries

    Functions
    1. Execute concurrent web searches using tavily API
    2. Deduplicates and format

    Args:
        state: Current graph state containing the search query

    Returns:
        Command: To help update the graph state AND route to the next node
    """

    # User query
    user_query = state.user_query

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    max_search_results = configurable.max_search_results
    assistant_role = configurable.assistant_role

    # Search tasks
    search_tasks = []
    for query in state.search_queries:
        search_tasks.append(
            tavily_async_client.search(
                query,
                max_results=max_search_results,
                include_raw_content=True,
                topic="general",
            )
        )

    # Execute all searches concurrently
    search_docs = await asyncio.gather(*search_tasks)

    # Deduplicate and format sources
    deduplicated_search_docs = deduplicate_sources(search_docs)
    source_str = format_sources(
        deduplicated_search_docs, max_tokens_per_source=1000, include_raw_content=True
    )

    # Generate structured notes relevant to the extraction schema
    system_instruction = SUMMARIZE_INSTRUCTIONS.format(
        user_query=user_query,
        assistant_role=assistant_role,
        content=source_str,
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(
                content=f"Take clear, organized notes about the user query, focusing on topics relevant to our interests "
            ),
        ]
    )

    if configurable.include_search_results:
        return Command(
            update={
                "completed_notes": [str(response.content)],
                "search_results": deduplicated_search_docs,
            },
            goto="extract_info",
        )
    else:
        return Command(
            update={"completed_notes": [str(response.content)]},
            goto="extract_info",
        )


async def extract_info(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["reflection"]]:
    """Langgraph node that extract required information in the schema fields.

    Uses an LLM to create or update a running summary based on the newest web research
    results, integrating them with any existing summary

    Args:
        state: Current graph containing research topic, running summary, and web research results


    """

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    assistant_role = configurable.assistant_role

    # Format all notes
    web_research_notes = format_all_notes(state.completed_notes)

    system_instruction = EXTRACTION_PROMPT.format(
        assistant_role=assistant_role,
        web_research_notes=web_research_notes,
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(content=f"Produce a structured output from the nodes"),
        ]
    )

    return Command(update={"info": response}, goto="reflection")


async def reflection(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["format_response", "web_research"]]:
    """Langgraph node that identifies knowledge gaps and generates follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    a new search query to address those gaps. uses structured output to extract the follow-up query in JSON format

    Args:
        state: Current graph state containing the running research output and user query

    Returns:
        _type_: _description_
    """

    # user Query
    user_query = state.user_query

    # extracted info
    extracted_information = state.info


    # Get Configuration
    configuration = Configuration.from_runnable_config(config)
    max_reflection_steps = configuration.max_reflection_steps
    assistant_role = configuration.assistant_role

    system_instruction = REFLECTION_INSTRUCTIONS.format(
        user_query=user_query,
        assistant_role=assistant_role,
        extracted_information=extracted_information,
    )

    structured_llm = llm.with_structured_output(ReflectionOutput)

    response = await structured_llm.ainvoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(
                content=f"Analyse the information and return a structured output"
            ),
        ]
    )

    if response.is_satisfactory:
        return Command(
            update={"is_satisfactory": response.is_satisfactory},
            goto="format_response",
        )
    else:
        # Check if we have hit max reflection count
        if state.reflection_steps_taken <= max_reflection_steps:

            return Command(
                update={
                    "is_satisfactory": response.is_satisfactory,
                    "search_queries": response.search_queries,
                    "reflection_steps_taken": state.reflection_steps_taken + 1,
                },
                goto="web_research",
            )

        else:

            return Command(goto="format_response")
        
async def format_response(state: AgentState, config: RunnableConfig)->Command[Literal[END]]:
    """_summary_

    Args:
        state (AgentState): _description_

    Returns:
        Command[Literal[END]]: _description_
    """
    
    #Get extracted info
    extracted_info = state.info
    
    configuration = Configuration.from_runnable_config(config)
    assistant_role = configuration.assistant_role
    
    
    user_query = state.user_query
    
    system_instruction = FORMAT_RESPONSE_PROMPT.format(
        user_query = user_query,
        assistant_role = assistant_role,
        relevant_information = extracted_info
    )
    
    response = await llm.ainvoke([SystemMessage(content=system_instruction)])
    
    
    return Command(
        update={"messages": [response]},
        goto=END
    )


graph_builder = StateGraph(
    AgentState, input=InputState, output=OutputState, config_schema=Configuration
)

graph_builder.add_node("agent", agent)
graph_builder.add_node("generate_queries", generate_queries)
graph_builder.add_node("web_research", web_research)
graph_builder.add_node("extract_info", extract_info)
graph_builder.add_node("reflection", reflection)
graph_builder.add_node("format_response", format_response)


graph_builder.set_entry_point("agent")


app = graph_builder.compile()
