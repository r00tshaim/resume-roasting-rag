from fastapi import FastAPI, UploadFile

from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.worker import process_file
from bson import ObjectId

app = FastAPI()

@app.get("/")
def hello():
    return {"status": "healthy"}

@app.get("/status")
async def get_file_status(id: str):
    file_in_db = await files_collection.find_one(
        filter={"_id": ObjectId(id)}
    )
    if not file_in_db:
        return {"error": "File not found"}
    return {
        "file_id": str(file_in_db["_id"]),
        "file_name": file_in_db.get("name"),
        "status": file_in_db.get("status"),
        "result": file_in_db.get("result")
    }

@app.post("/upload")
async def upload_file(file: UploadFile):

    #save file path to database
    #When you call insert_one, it returns an object with the inserted document’s ID, but not the full document itself.
    file_in_db = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving"
        ),
    )

    id = str(file_in_db.inserted_id)

    file_path = f"/mnt/uploads/{id}/{file.filename}"

    # Save the file to disk
    await save_to_disk(file, file_path)

    #Push to queue
    q.enqueue(process_file, id, file_path)

    #update file status to 'queued'
    await files_collection.update_one(
        filter={"_id": file_in_db.inserted_id},
        update={"$set": {"status": "queued"}}
    )

    return {"file_id": id, "file_name": file.filename}