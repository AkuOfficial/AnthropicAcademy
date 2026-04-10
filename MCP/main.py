import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from MCP.mcp_client import MCPClient
# from MCP.core.claude import Claude
from MCP.core.gemini import GeminiService

from MCP.core.cli_chat import CliChat
from MCP.core.cli import CliApp

load_dotenv()

# model = os.getenv("CLAUDE_MODEL", "")
model = os.getenv("GEMINI_MODEL", "")
# api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_key = os.getenv("GOOGLE_API_KEY", "")

# assert model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert model, "Error: GEMINI_MODEL cannot be empty. Update .env"
# assert api_key, "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
assert api_key, "Error: GOOGLE_API_KEY cannot be empty. Update .env"


async def main():
    claude_service = GeminiService(model=model, api_key=api_key)

    server_scripts = sys.argv[1:]
    clients = {}

    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "mcp_server.py")

    command, args = (
        ("uv", ["run", server_path])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", server_path)
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    # if sys.platform == "win32":
    #     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
