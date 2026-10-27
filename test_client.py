import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            resources = await session.list_resources()
            print("RESOURCES:", [str(r.uri) for r in resources.resources])

            prompts = await session.list_prompts()
            print("PROMPTS:", [p.name for p in prompts.prompts])

            print("\n--- search_incidents (high) ---")
            r = await session.call_tool("search_incidents", {"severity": "high"})
            print(r.content[0].text)

            print("\n--- stats://summary ---")
            s = await session.read_resource("stats://summary")
            print(s.contents[0].text)


asyncio.run(main())