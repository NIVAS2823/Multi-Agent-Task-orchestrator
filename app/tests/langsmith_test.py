from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

import os 


os.environ['LANGSMITH_TRACING'] = "true"
os.environ['LANGSMITH_PROJECT'] = "multi-agent-orchestrator"


llm = ChatOpenAI(model='gpt-4o-mini',temperature=0)

response = llm.invoke([HumanMessage(content="Say hello in one sentence")])

print(response)
