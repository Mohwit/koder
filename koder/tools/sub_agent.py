"""Sub agent tool for the Koder agent."""

import os

from koder.agent.agent import Agent
from koder.prompts.sub_agent_prompt import system_prompt


def sub_agent(query: str) -> Agent:
    """Create a sub agent with the given API key and tools."""
    from koder.tools.tools_schema import tools_schema # noqa: F401

    agent = Agent(
        model="claude-sonnet-4-20250514",
        base_url="https://api.anthropic.com/v1",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        system_prompt=system_prompt,
        tools=tools_schema,
    )
    response = agent.query(query)
    if response["tool_calls"]:
        print(f"\n🛠️  Tool calls executed: {len(response['tool_calls'])}")

    return response["content"]
