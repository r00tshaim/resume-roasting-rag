from typing import TypedDict
from pydantic import Field
from pymongo.asynchronous.collection import AsyncCollection
from app.db.db import database

class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file (e.g., 'uploaded', 'processed')")
    result: str = Field(..., description="Roasting message from LLM")

# a collection in MongoDB is similar to a table in SQL databases.
COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]