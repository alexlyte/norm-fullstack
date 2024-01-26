# main.py
from fastapi import FastAPI, Query
from app.utils import Output

app = FastAPI()

"""
Please create and endpoint that accepts a query string, e.g., "what happens if I steal 
from the Sept?" and returns a JSON response serialized from the Pydantic Output class.
"""