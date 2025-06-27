import base64
import os
from ..db.collections.files import files_collection
from bson import ObjectId
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    print("***********API KEY not found**************************")
    exit(0)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    # other params...
)


def encode_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    return encoded_image


async def roast_with_llm(id: str):

    images_path_prefix = f"/mnt/uploads/images/{id}"

    # List all files in the directory
    image_files = [
        os.path.join(images_path_prefix, fname)
        for fname in os.listdir(images_path_prefix)
        if os.path.isfile(os.path.join(images_path_prefix, fname))
    ]

    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"status": "encoding images to base64"}}
    )

    # Capture base64 of all images in a single list
    all_encoded_images = [
        encode_image(image_file_path)
        for image_file_path in image_files
    ]

    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"status": "handing over to llm"}}
    )

    message_local = HumanMessage(
       content=[
            {"type": "text", "text": "Given images are of candidate resume, You are a funny mentor I want you to roast this resume"},
            *[
                {"type": "image_url", "image_url": f"data:image/png;base64,{encoded_image}"}
                for encoded_image in all_encoded_images
            ]
        ]
    )

    result_local = llm.invoke([message_local])

    await files_collection.update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "status": "handling by llm success",
                "result": result_local.content  # Save LLM response to 'response' field
            }
        }
    )