from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langsmith import traceable

MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"


@tool
def get_product_price(product: str) -> float:
    """Look up the price of a product in the catalog."""
    print (f" >>Executing get_product_price(product='{product}')")
    prices= {'Laptop': 85749.0, 'Mobile_phone':20000.00, 'Television':75999.00, 'Refridgerator': 69999.0}
    return prices.get(product,0)

@tool
def apply_discount(price: float, discount_tier: str)-> float:
    """Apply a discount_tier to the price and return final price. Available tiers are Bronze, Silver,Gold"""
    print (f" >> Executing discount over price( price={price}, discount_tier ='{discount_tier}')")
    discount_percentages = {'bronze': 5,'silver': 12, 'gold':23}
    discount = discount_percentages.get(discount_tier,0)
    return round(price*(1-discount/100),2)

@traceable(name="Langchain Agent Loop")
def run_agent( questions: str): 
    # print(f"{questions=}")
    tools =[get_product_price, apply_discount]
    tools_dict={t.name : t for t in tools}

    llm= init_chat_model(f"ollama:{MODEL}", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    print(f"Question: {questions}")
    print("="*50)

    messages = [ 
        SystemMessage(content=(
            "You are a helpful shopping assistant"
            "You have access to product catalog tool and a discount tool.\n\n"
            "STRICT RULES = you must follow these exactly:\n"
            "1. Never Guess or assume any product price"
            "You must call the get_product_price tool to get the real price.\n"
            "2. Only call apply_discount AFTER you have received price from " \
            "get_product_price. Pass the exact price returned by get_product_price" \
            "- do not pass made up number.\n"
            "3. NEVER calculate discounts yourself using math." \
            "Always use the apply_discount tool. \n"
            "4. If the user doesnt specify the discount tier, " \
            "ask the user to specify one, don't assume yourself\n"
         ))
         ,
         HumanMessage(content=questions)

         
    ]



if __name__=="__main__":
    print("Hello from Langchain Agent (.bind_tools)")
    print()
    result= run_agent("what is the price of Laptop after applying a gold discount")



