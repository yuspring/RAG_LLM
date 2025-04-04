import warnings
from dotenv import load_dotenv
from langchain_community.chat_models import ChatDeepInfra
from langchain_community.embeddings import DeepInfraEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph, END
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore")
load_dotenv()

llm = ChatDeepInfra(model="meta-llama/Llama-3.3-70B-Instruct")
embeddings = DeepInfraEmbeddings(model_id="BAAI/bge-m3")
vector_store = InMemoryVectorStore(embeddings)


# Item 1: 天然備長碳
item_1 = Document(
    page_content=
    """ 
    品項:天然備長碳\n
    金額:250\n
    數量:10\n
    是否上架:是
    """ 
)

# Item 2: 自然風隨心袋
item_2 = Document(
    page_content=
    """ 
    品項:自然風隨心袋\n
    金額:200\n
    數量:5\n
    是否上架:是
    """ 
)

# Item 3: 嫩嫩粉兩用杯
item_3 = Document(
    page_content=
    """ 
    品項:嫩嫩粉兩用杯\n    
    金額:100\n
    數量:3\n
    是否上架:否
    """ 
)

# Item 4: 湛霧灰兩用杯
item_4 = Document(
    page_content=
    """ 
    品項:湛霧灰兩用杯\n
    金額:300\n
    數量:5\n
    是否上架:是
    """ 
)

# Item 5: 暖暖橘馬克杯
item_5 = Document(
    page_content=
    """ 
    品項:暖暖橘馬克杯\n
    金額:150\n
    數量:3\n
    是否上架:是
    """ 
)

# Item 6: 霧黑色手沖壺
item_6 = Document(
    page_content=
    """ 
    品項:霧黑色手沖壺\n
    金額:250\n
    數量:1\n
    是否上架:否
    """ 
)

# Item 6: 霧黑色手沖壺
item_7 = Document(
    page_content=
    """ 
    品項:櫻花粉手沖壺\n
    金額:100\n
    數量:2\n
    是否上架:否
    """ 
)

# Item 8: 有機肉桂咖啡+
item_8 = Document(
    page_content=
    """ 
    品項:有機肉桂咖啡\n
    金額:100\n
    數量:30\n
    是否上架:是
    """ 
)

Item_list = [
    item_1,
    item_2,
    item_3,
    item_4,
    item_5,
    item_6,
    item_7,
    item_8,
]

vector_store.add_documents(documents=Item_list)
prompt = PromptTemplate.from_template(
"""
    # Tasks 
    你的主要任務是閱讀RAG_DATA，並嚴格且僅根據RAG_DATA來回答USER_RESPONSE
    在整個回答中扮演 PLAY_ROLE 中定義的角色

    # Data Context
    1. PLAY_ROLE: 扮演的角色設定
    2. RAG_DATA: 產生答案的資訊來源
    3. USER_RESPONSE: 使用者的回覆

    # Input
    PLAY_ROLE: <PLAY_ROLE> {PLAY_ROLE} </PLAY_ROLE>
    RAG_DATA: <RAG_DATA> {RAG_DATA} </RAG_DATA>
    USER_RESPONSE: <USER_RESPONSE> {USER_RESPONSE} </USER_RESPONSE>
""")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve_node(state: State):
    print("---RAG Retrieve---")
    retrieved_docs = vector_store.similarity_search(state["question"], k=min(10,len(Item_list)))
    return {"context": retrieved_docs}

def generate_node(state: State):
    print("---RAG Generate---")
    docs_content = "\n---\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({
        "PLAY_ROLE": "你是一名商店助手的LLM", 
        "RAG_DATA": docs_content, 
        "USER_RESPONSE": state["question"],
    })
    response = llm.invoke(messages)
    return {"answer": response.content}



graph_builder = StateGraph(State)

graph_builder.add_node("retrieve_node", retrieve_node)
graph_builder.add_node("generate_node", generate_node)

graph_builder.add_edge(START, "retrieve_node")
graph_builder.add_edge("retrieve_node", "generate_node")
graph_builder.add_edge("generate_node", END)
graph = graph_builder.compile()

user_input = str(input("User Input:"))
response = graph.invoke({"question": user_input})
print(response["answer"])