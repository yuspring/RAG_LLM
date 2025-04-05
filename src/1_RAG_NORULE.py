import warnings
import DB_mongo
import LLM_router
from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph, END
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class RAG_Agent:
    def __init__(self,VENDOR,MODEL,EMBEDDING_MODEL,URL=None):

        warnings.filterwarnings("ignore")
        load_dotenv()
        self.llm = LLM_router.chat_model(VENDOR,MODEL)
        self.embeddings = LLM_router.embedding_model(VENDOR,EMBEDDING_MODEL)
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.vector_store.add_documents(documents=DB_mongo.get_all_items())
        self.retrieve_num = 10
        with open("./prompt/prompt-norule-ch.txt", 'r', encoding='utf-8') as file:
            self.prompt = PromptTemplate.from_template(file.read())

        with open("./prompt/store-rag-role.txt", 'r', encoding='utf-8') as file:
            self.rag_play_role = file.read()
    
        self.graph = self._build_graph()
        
    def _build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("retrieve_node", self._retrieve_node)
        graph_builder.add_node("generate_node", self._generate_node)

        graph_builder.add_edge(START, "retrieve_node")
        graph_builder.add_edge("retrieve_node", "generate_node")
        graph_builder.add_edge("generate_node", END)
        return graph_builder.compile()

    def _retrieve_node(self,state: State):
        print("---RAG Retrieve---")
        retrieved_docs = self.vector_store.similarity_search(state["question"], k=self.retrieve_num)
        return {"context": retrieved_docs}

    def _generate_node(self,state: State):
        print("---RAG Generate---")
        docs_content = "\n---\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke({
            "PLAY_ROLE": self.rag_play_role, 
            "RAG_DATA": docs_content, 
            "USER_RESPONSE": state["question"],
        })
        response = self.llm.invoke(messages)
        return {"answer": response.content}

    def query(self, question):
        response = self.graph.invoke({"question": question})
        return response["answer"]

VENDOR="DEEPINFRA"
MODEL="meta-llama/Llama-3.3-70B-Instruct"
EMBEDDING_MODEL="BAAI/bge-m3"

LLM_agent = RAG_Agent(VENDOR,MODEL,EMBEDDING_MODEL)
print(LLM_agent.query("你好"))