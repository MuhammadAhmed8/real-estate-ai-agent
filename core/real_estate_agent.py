import uuid

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from config import Config
from core.llm.llm_factory import LLMFactory
from core.nodes.chat import chat_node, build_chatbot_node
from core.state.conversation_stage import ConversationStage
from core.state.state import State
from core.tools import kick_ass_tool, save_customer_preferences_tool

class RealEstateAgent:
    def __init__(self, llm=None):
        self.name = "real_estate_agent"
        self.description = "A real estate agent who helps clients buy and sell properties."
        self.llm = llm
        self.llm_with_tools = None
        self.graph = None
        self.tools = []
        self.memory = MemorySaver()

    async def setup(self):
        Config.validate()

        if self.llm is None:
            self.llm = LLMFactory.create()

        self.tools = [save_customer_preferences_tool, kick_ass_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        await self.__build_graph()

    async def __build_graph(self):
        graph_builder = StateGraph(State)
        tools_node = ToolNode(self.tools)

        graph_builder.add_node("chatbot", build_chatbot_node(self.llm_with_tools))
        graph_builder.add_node("tools", tools_node)

        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge("chatbot", END)

        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def process_message(self, message: str, thread_id: str = None):

        if not thread_id:
             thread_id = str(uuid.uuid4())

        configuration = {
            "configurable": {"thread_id": thread_id}
        }

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "conversation_stage": ConversationStage.GREETING
        }

        result = await self.graph.ainvoke(initial_state, config=configuration)

        messages = result.get("messages", [])
        response = messages[-1]
        # print(result)
        return {
            "response": response,
            "conversation_stage": result.get("conversation_stage", ConversationStage.GREETING)
        }


    # 3 bed flat with parking in Karachi for 2.5 crores with balcony and garden in Gulshan Iqbal
