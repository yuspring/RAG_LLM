import pymongo
from langchain_core.documents import Document

def get_all_items():
    client = pymongo.MongoClient('mongodb://localhost:27017')
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