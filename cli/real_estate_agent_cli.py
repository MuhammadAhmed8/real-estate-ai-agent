from core.real_estate_agent import RealEstateAgent


class RealEstateAgentCli:
    def __init__(self):
        self.commands = {
            'list': self.list_properties,
            'add': self.add_property,
            'remove': self.remove_property,
            'help': self.show_help,
            'exit': self.exit_cli
        }
        self.properties = []
        self.agent = RealEstateAgent()

    async def setup(self):
        print("🏠 Initializing Real Estate AI Agent...")
        await self.agent.setup()
        print("✅ Agent ready! I'm Sarah, your personal real estate assistant.")
        print("💡 Type 'help' for commands, 'quit' to exit, or just start chatting!")
        print("-" * 60)

    def list_properties(self, args):
        if not self.properties:
            print("No properties available.")
            return
        for idx, prop in enumerate(self.properties, 1):
            print(f"{idx}. {prop}")

    def add_property(self, args):
        if not args:
            print("Usage: add <property_description>")
            return
        property_description = ' '.join(args)
        self.properties.append(property_description)
        print(f"Property added: {property_description}")

    def remove_property(self, args):
        if not args or not args[0].isdigit():
            print("Usage: remove <property_number>")
            return
        property_number = int(args[0])
        if 1 <= property_number <= len(self.properties):
            removed_property = self.properties.pop(property_number - 1)
            print(f"Property removed: {removed_property}")
        else:
            print("Invalid property number.")

    def show_help(self, args):
        print("Available commands:")
        for command in self.commands:
            print(f" - {command}")

    def exit_cli(self, args):
        print("Exiting Real Estate Agent CLI.")
        exit(0)

    async def run(self):
        await self.setup()
        print("Welcome to the Real Estate Agent CLI. Type 'help' for a list of commands.")

        while True:
            user_input = input("> ").strip()
            if not user_input:
                continue
            user_input = user_input.lower()

            if user_input in self.commands:
                self.commands[user_input](None)
                continue

            result = await self.agent.process_message(user_input, "1")

            print(result["response"])

