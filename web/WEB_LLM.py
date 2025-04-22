import sys
sys.path.insert(0,'.')
from flask import Flask, render_template, request, jsonify, redirect,url_for
import LLM.RAG_JUDGE
from LLM.LLM_config import LLM_config

def get_llm_response(user_message):

    print(f"收到的訊息: {user_message}")
    response = judge_agent.query(user_message)
    print(f"LLM 回應: {response}")

    return response


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "沒有收到訊息"}), 400

    bot_response = get_llm_response(user_message)
    return jsonify({"response": bot_response})



if __name__ == "__main__":
    app.run(debug=True, port=8000)
    VENDOR="DEEPINFRA"
    MODEL="meta-llama/Llama-3.3-70B-Instruct"
    EMBEDDING_MODEL="BAAI/bge-m3"
    judge_agent = LLM.RAG_JUDGE.RAG_Judge_Agent(VENDOR,MODEL,EMBEDDING_MODEL)