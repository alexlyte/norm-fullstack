from utils import Output, DocumentService, QdrantService
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ItemQuery(BaseModel):
    item_query: str

@app.post("/query")
async def query(item: ItemQuery) -> Output:

    doc_serivce = DocumentService("../docs/") # implemented
    docs = doc_serivce.create_documents(parse_files=False) # implemented

    index = QdrantService(k=3) # implemented
    index.connect() # implemented
    index.load(docs) # implemented

    return index.query(item.item_query) # NOT implemented

