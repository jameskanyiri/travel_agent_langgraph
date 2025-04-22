import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


DEFAULT_ROLE = """
Help user understand the following documents when traveling between countries:

 1. Visa Requirements, 
 2. Passport Requirements, 
 3. Travel Advisories, 
 4. Additional Documents.
"""

DEFAULT_OUTPUT_STRUCTURE = """
Use this structure to create a report on the user-provided query:

1. Visa Requirements, 
    - Well formatted points
2. Passport Requirements, 
    - Well formatted points
3. Travel Advisories, 
    - Well formatted points
4. Additional Documents.
    - Well formatted points
 
"""


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the assistant."""

    user_name: str = "James"

    assistant_name: str = "GlobeGuide"

    assistant_role: str = DEFAULT_ROLE
    
    output_structure: str = DEFAULT_OUTPUT_STRUCTURE

    # Max search queries per user query
    max_search_queries: int = 1

    # Max search results per query
    max_search_results: int = 1

    # Max reflection steps
    max_reflection_steps: int = 3

    # Whether to include search results in the output
    include_search_results: bool = True

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
