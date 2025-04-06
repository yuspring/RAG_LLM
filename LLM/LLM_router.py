from langchain_community.chat_models import ChatDeepInfra, ChatOllama
from langchain_community.embeddings import DeepInfraEmbeddings, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class LLM_router:
    def chat_model(NAME,MODEL,URL=None):
        if(NAME=='OPENAI'):
            return ChatOpenAI(model=MODEL,max_tokens=4096,temperature=0.3)
        
        if(NAME=='DEEPINFRA'):
            return ChatDeepInfra(model=MODEL,max_tokens=4096,temperature=0.3)
        
        if (NAME=='OLLAMA'):
            return ChatOllama(model=MODEL,base_url=URL,max_tokens=4096,temperature=0.3)

    def embedding_model(NAME,MODEL,URL=None):
        if(NAME=='OPENAI'):
            return OpenAIEmbeddings(model=MODEL)
        
        if (NAME=='DEEPINFRA'):
            return DeepInfraEmbeddings(model_id=MODEL)
        
        if (NAME=='OLLAMA'):
            return OllamaEmbeddings(model=MODEL,base_url=URL)

# openai model: gpt-4o
# openai embedding: text-embedding-3-large

# deepinfra model: meta-llama/Llama-3.3-70B-Instruct, deepseek v3 or deepseek r1
# deepinfra embedding: BAAI/bge-m3
# https://api.deepinfra.com/v1/openai/chat/completions

# ollama model: gemma3 , llama3.2
# ollama embedding: nomic-embed-text