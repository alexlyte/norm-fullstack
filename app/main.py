from utils import Output, DocumentService, QdrantService
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ItemQuery(BaseModel):
    item_query: str

@app.post("/query")
async def query(item: ItemQuery) -> Output:

    doc_serivce = DocumentService("../docs/", "../text_docs/")
    docs = doc_serivce.create_documents(parse_files=False)

    index = QdrantService(k=3)
    index.connect()
    index.load(docs)

    return index.query(item.item_query)

