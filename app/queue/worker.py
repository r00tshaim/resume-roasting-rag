from ..db.collections.files import files_collection
from bson import ObjectId
import os
from ..ai.llm import run_resume_fit_analysis
from .q import q

from pdf2image import convert_from_path


async def update_db_sync(id, results):
    llm_result = results["llm_result"]

    # Convert Pydantic object to dict
    result_dict = llm_result.dict()

    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "response": result_dict,
            "status": "processed by llm"
            }
        }
    )

    print(f"[MongoDB] Updated response for id {id}")

async def process_llm(id, jd):
    results = run_resume_fit_analysis(id, jd)
    await update_db_sync(id, results)


async def process_file(id: str, file_path: str):

    print(f"Processing file with ID: {id}")

    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"status": "processing"}}
    )


    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"status": "converting to images"}}
    )

    #Step1: Convert the pdf to image
    pages = convert_from_path(file_path)


    image_save_path_prefix = f"/mnt/uploads/images/{id}/"
    # Ensure the directory exists
    os.makedirs(os.path.dirname(image_save_path_prefix), exist_ok=True)

    for i,page in enumerate(pages):
        image_save_path = image_save_path_prefix + f"image-{i}.jpg"
        page.save(image_save_path, 'JPEG')


    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"status": "converting to images success"}}
    )

    entry = await files_collection.find_one(
        filter={"_id": ObjectId(id)}
    )

    jd = entry["job_description"]

    #give to llm
    q.enqueue(process_llm,id, jd)


