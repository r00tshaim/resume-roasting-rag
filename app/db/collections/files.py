from typing import TypedDict
from pydantic import Field
from pymongo.asynchronous.collection import AsyncCollection
from app.db.db import database

class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    job_description: str = Field(..., description="Job description of the role for which user provided the resume")
    status: str = Field(..., description="Status of the file (e.g., 'uploaded', 'processed')")
    response: dict = Field(..., description="Results from LLM")

# a collection in MongoDB is similar to a table in SQL databases.
COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]