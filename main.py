import asyncio

from cli.real_estate_agent_cli import RealEstateAgentCli

async def main():
    cli = RealEstateAgentCli()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())