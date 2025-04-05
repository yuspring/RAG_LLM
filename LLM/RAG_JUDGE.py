from LLM.DB_mongo import DB_mongo
from LLM.LLM_router import LLM_router
from prompt.prompt_template import prompt as pt

import re
import json
import datetime
import warnings
from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph, END
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate

class State(TypedDict):
    question: str
    rag_data: List[Document]
    rag_answer: str
    judge_answer: str
    judge_regex: tuple
    answer : str

class RAG_Judge_Agent:
    def __init__(self,VENDOR,VENDOR_EMBEDDING,MODEL,EMBEDDING_MODEL,URL=None,ENBEDDING_URL=None):
        warnings.filterwarnings("ignore")
        load_dotenv()

        self.RETRIEVE_NUM=10
        self.llm = LLM_router.chat_model(VENDOR,MODEL)
        self.embeddings = LLM_router.embedding_model(VENDOR_EMBEDDING,EMBEDDING_MODEL)
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.vector_store.add_documents(documents=DB_mongo.get_DBdata())

        self.prompt_rag = PromptTemplate.from_template(pt.PROMPT_RULE_CHINESE)
        self.prompt_judge = PromptTemplate.from_template(pt.PROMPT_JUDGE_CHINESE)
        self.rag_play_role = pt.STORE_RAG_ROLE_CHINESE
        self.rag_rules = pt.STORE_RAG_RULES_CHINESE

        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(State)

        graph_builder.add_node("rag_retrieve_node", self._rag_retrieve_node)
        graph_builder.add_node("rag_generate_node", self._rag_generate_node)
        graph_builder.add_node("judge_node", self._judge_node)
        graph_builder.add_node("regex_tool", self._regex_tool)
        graph_builder.add_node("log_node", self._log_node)
        graph_builder.add_node("answer_node", self._answer_node)
        graph_builder.add_node("reject_node", self._reject_node)

        graph_builder.add_edge(START, "rag_retrieve_node")
        graph_builder.add_edge("rag_retrieve_node", "rag_generate_node")
        graph_builder.add_edge("rag_generate_node", "judge_node")
        graph_builder.add_edge("judge_node", "regex_tool")
        graph_builder.add_edge("regex_tool", "log_node")

        graph_builder.add_conditional_edges(
            "regex_tool",
            self._score_condition,
            {
                "answer": "answer_node",
                "reject": "reject_node"
            }
        )

        graph_builder.add_edge("log_node", END)
        graph_builder.add_edge("answer_node", END)
        graph_builder.add_edge("reject_node", END)
        return graph_builder.compile()
    def _rag_retrieve_node(self,state: State):
        print("---RAG Retrieve---")
        retrieved_docs = self.vector_store.similarity_search(state["question"], k=self.RETRIEVE_NUM)
        return {"rag_data": retrieved_docs}

    def _rag_generate_node(self,state: State):
        print("---RAG Generate---")
        docs_content = "\n---\n".join(doc.page_content for doc in state["rag_data"])
        input_data = {
            "PLAY_ROLE": self.rag_play_role, 
            "RAG_DATA": docs_content, 
            "USER_RESPONSE": state["question"],
            "RULES": self.rag_rules,
        }
        messages = self.prompt_rag.invoke(input_data)
        response = self.llm.invoke(messages)
        return {"rag_answer": response.content}

    def _judge_node(self,state: State):
        print("---RAG Judge---")
        messages = self.prompt_judge.invoke({
            "LLM_RULES": self.rag_rules,
            "USER_MESSAGE":state["question"],
            "LLM_MESSAGE": state["rag_answer"],
        })
        response = self.llm.invoke(messages)
        return {"judge_answer": response.content}

    def _regex_tool(self,state: State):
        print("---Regex Tool---")
        print(state["judge_answer"])
        score = re.search(r"分數:\s*(\d+)", state["judge_answer"]).group(1)
        tag = re.search(r"標籤:\s*(.*)", state["judge_answer"]).group(1)
        context = re.search(r"簡述:\s*(.*)", state["judge_answer"]).group(1)
        judge_info = (int(score), tag, context)
        return {"judge_regex" : judge_info}

    def _log_node(self,state: State):
        print("---Log Node---")
        log = {
            "score": state["judge_regex"][0],
            "tag": state["judge_regex"][1],
            "context": state["judge_regex"][2],
        }
        time = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        with open(f"./log/{time}.json",'w',encoding='utf-8') as f:
            json.dump(log, f, indent=4)

    def _score_condition(self,state: State):
        print("---Score condition---")
        if(state["judge_regex"][0] >= 3):
            return "answer"
        else:
            return "reject"

    def _answer_node(self,state: State):
        print("---Answer Node---")
        return{"answer": state["rag_answer"]}

    def _reject_node(self,state: State):
        print("---Reject Node---")
        return{"answer": "你的問題我無法回答"}

    def query(self, question):
        response = self.graph.invoke({"question": question})
        return response["answer"]