"""Entry point for running the Koder Agent CLI.

This module sets up available tool functions, constructs the Agent instance,
and starts an interactive loop that processes user prompts until the user exits.
"""

import os
import threading
from dotenv import load_dotenv

from koder.agent.agent import Agent
from koder.prompts.main_agent_prompt import system_prompt
from koder.tools.main_agent_tools_schema import tools_schema
from koder.utils.inialize_code_rag import initialize_code_rag
from koder.utils.query_constructions import construct_query
load_dotenv()


def main() -> None:
    """Run the interactive Koder Agent CLI loop until the user exits."""
    threading.Thread(target=initialize_code_rag, daemon=True).start()
    # Create the agent with proper configuration
    agent = Agent(
        model="claude-3-7-sonnet-20250219",
        base_url="https://api.anthropic.com/v1",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        system_prompt=system_prompt,
        tools=tools_schema,
    )

    print("🤖 Koder Agent is ready! Type 'quit' to exit.")
    print("=" * 50)

    while True:
        try:
            user_prompt = input("\n💬 Enter your prompt: ")

            if user_prompt.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not user_prompt.strip():
                continue

            print("\n🔄 Processing...")
            
            ## add context to the user prompt
            constructed_query = construct_query(user_prompt)
            response = agent.query(constructed_query)

            print("\n🤖 Response:")
            print("-" * 30)
            print(response["content"])

            if response["tool_calls"]:
                print(f"\n🛠️  Tool calls executed: {len(response['tool_calls'])}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except (OSError, ValueError, RuntimeError) as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    main()
