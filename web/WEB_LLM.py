import sys
import os
import glob
import json
from flask import Flask, render_template, request, jsonify, redirect,url_for

sys.path.insert(0,'.')
import LLM.RAG_JUDGE
from LLM.LLM_config import LLM_config

app = Flask(__name__)



def get_color_for_score(score):
  
  score_int = int(float(score)) 
  if score_int in (1, 2):
    return 'red'
  elif score_int == 3:
    return 'orange'
  elif score_int in (4, 5):
    return 'green'

def get_llm_response(user_message):

    print(f"收到的訊息: {user_message}")
    response = judge_agent.query(user_message)
    print(f"LLM 回應: {response}")
    return response


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

@app.route('/log')
def display_all_json_data():

  all_processed_data = []
  json_files = glob.glob(os.path.join('./log', '*.json'))
  for file_path in json_files:
    
    with open(file_path, 'r', encoding='utf-8') as f:
      item_data = json.load(f)

    processed_item = item_data.copy()
    score = item_data['score'] 
    color = get_color_for_score(score) 
    
    processed_item['text_color'] = color
    all_processed_data.append(processed_item)

  return render_template('log.html', data_list=all_processed_data)


@app.route('/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        current_config = config_manager.get_all_data()
        return render_template('config.html', config_data=current_config)
    if request.method == 'POST':
        for key in request.form:
            value = request.form[key]
            config_manager.edit(key, value)
        return redirect(url_for('handle_config'))




if __name__ == "__main__":
    config_manager = LLM_config()
    VENDOR = config_manager.load("VENDOR")
    MODEL = config_manager.load("MODEL")
    EMBEDDING_MODEL = config_manager.load("EMBEDDING_MODEL")
    VENDOR_EMBEDDING_MODEL = config_manager.load("VENDOR_EMBEDDING_MODEL")
    judge_agent = LLM.RAG_JUDGE.RAG_Judge_Agent(VENDOR,VENDOR_EMBEDDING_MODEL,MODEL,EMBEDDING_MODEL)
    app.run(debug=True, port=8000)
    