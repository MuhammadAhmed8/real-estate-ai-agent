from typing import List

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import Annotated

from core.state.conversation_stage import ConversationStage

class State(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    conversation_stage: ConversationStage

    def is_new_conversation(self) -> bool:
        return len(self.messages) <= 1

    def get_last_message(self) -> str | None:
        if self.messages and len(self.messages) > 0:
            return self.messages[-1].content.lower()
        return None
