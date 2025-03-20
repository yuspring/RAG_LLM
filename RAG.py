import os
from dotenv import load_dotenv
from langchain import hub
from langchain_community.chat_models import ChatDeepInfra
from langchain_community.embeddings import DeepInfraEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

load_dotenv()

llm = ChatDeepInfra(model="meta-llama/Llama-3.3-70B-Instruct")
embeddings = DeepInfraEmbeddings(model_id="BAAI/bge-m3")
vector_store = InMemoryVectorStore(embeddings)


document_1 = Document(
    page_content="這間早餐店的店名叫做家鄉早餐店",
)

documents = [
    document_1,
]

vector_store.add_documents(documents=documents)

prompt = hub.pull("rlm/rag-prompt")


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "早餐店店名叫什麼?"})
print(response["answer"])