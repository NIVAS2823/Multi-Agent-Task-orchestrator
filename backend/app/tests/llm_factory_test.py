
from langchain_core.messages import HumanMessage
from app.llm.factory import get_llm

from dotenv import load_dotenv

load_dotenv()

llm = get_llm()

# print(llm)

response = llm.invoke([
    HumanMessage(content="What is India's  California")
])

print(response.content)

