import pymongo
from .LLM_config import LLM_config 
from langchain_core.documents import Document

class DB_mongo:
    def get_all_items():
        config = LLM_config()
        client = pymongo.MongoClient(config.load("MONGODB_URL"))
        db = client.store
        collection = db.item

        db_item = collection.find() 
        Item_list = []

        for item in db_item:
            context = ""
            for key, value in item.items():
                if key == "_id":
                    continue
                context += f"{key}:{str(value)}\n"
            Item_list.append(Document(page_content=context))
        return Item_list