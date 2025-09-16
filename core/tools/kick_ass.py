from langchain_core.tools import tool


@tool
def kick_ass_tool(bad_word: str) -> None:
    """if user misbehaves, this tool kicks their ass"""
    print(f"Kicking user's ass {bad_word}")
