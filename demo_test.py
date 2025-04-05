from LLM.LLM_config import LLM_config
from LLM.RAG_NORULE import RAG_Agent as RAG_NoRule_Agent

VENDOR = LLM_config().load("VENDOR")
MODEL = LLM_config().load("MODEL")
EMBEDDING_MODEL = LLM_config().load("EMBEDDING_MODEL")

LLM_agent = RAG_NoRule_Agent(VENDOR,MODEL,EMBEDDING_MODEL)
print(LLM_agent.query("test"))
