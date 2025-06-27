from ..db.collections.files import files_collection
from bson import ObjectId
import os
from ..ai.llm import roast_with_llm
from .q import q

from pdf2image import convert_from_path

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

    #give to llm
    q.enqueue(roast_with_llm,id)


