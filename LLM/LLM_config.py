import json

class LLM_config:
    def __init__(self):
        self.FILE_PATH="./config/config.json"
        with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def load(self,key):
        return self.data[key]

    def edit(self,key,value):
        self.data[key] = value
        with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
