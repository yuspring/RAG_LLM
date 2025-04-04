import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')

db = client['store']
collection = db['item']

print(f"選擇了資料庫: {db.name}")
print(f"選擇了集合: {collection.name}")

document1 = {"test": 123}

insert_result = collection.insert_one(document1)