from typing import List
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()

import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

class Source(BaseModel):
    """Schema for source used by agent """

    url:str = Field(description="The URL of the source")

class AgentResponse(BaseModel):
    """Schema for agent response with sources"""

    answer:str = Field(description="The agent's answer to the query")
    source: List[Source]= Field(default_factory=List, description="The list of sources used to genetrae the answer")




llm = ChatOpenAI(
                model="grok-4",
                api_key=os.environ["XAI_API_KEY"],
                base_url="https://api.x.ai/v1",
                temperature=0
            )
tools = [TavilySearch()]
agent = create_agent(model =llm, tools=tools, response_format=AgentResponse)





def main():
    print("Hello from langchain-agent!")
    response = agent.invoke({"messages":HumanMessage(content="Who won FIFA 2026 worldcup?")})
    print(response)


if __name__ == "__main__":
    main()
