from langchain_community.chat_models import ChatDeepInfra, ChatOpenAI, ChatOllama
from langchain_community.embeddings import DeepInfraEmbeddings, OpenAIEmbeddings, OllamaEmbeddings


def chat_model(NAME,MODEL,URL=None):
    if(NAME=='OPENAI'):
        return ChatOpenAI(model=MODEL,base_url=URL)
    
    if(NAME=='DEEPINFRA'):
        return ChatDeepInfra(model=MODEL)
    
    if (NAME=='OLLAMA'):
        return ChatOllama(model=MODEL,base_url=URL)

def embedding_model(NAME,MODEL,URL=None):
    if(NAME=='OPENAI'):
        return OpenAIEmbeddings(model=MODEL,base_url=URL)
    
    if (NAME=='DEEPINFRA'):
        return DeepInfraEmbeddings(model_id=MODEL)
    
    if (NAME=='OLLAMA'):
        return OllamaEmbeddings(model=MODEL,base_url=URL)

# openai model: gpt-4o
# openai embedding: text-embedding-3-large

# deepinfra model: llama3.3, deepseek v3 or deepseek r1
# deepinfra embedding: BAAI/bge-m3

# ollama model: gemma3,llama3.2
# ollama embedding: nomic-embed-text