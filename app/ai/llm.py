import base64
import os
from dotenv import load_dotenv
from typing import List

from ..db.collections.files import files_collection
from bson import ObjectId

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field

from langgraph.graph import StateGraph

load_dotenv()

# ==== 1. LLM Output Model ====

class LLMResponse(BaseModel):
    right_fit: bool = Field(..., description="Is the candidate right fit for the job?")
    strengths: List[str] = Field(..., description="Candidate strengths")
    weaknesses: List[str] = Field(..., description="Candidate weaknesses")
    improvements: List[str] = Field(..., description="Areas for improvement")

# ==== 2. LLM Setup ====

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm = llm.with_structured_output(LLMResponse)

# ==== 3. Helpers ====

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ==== 4. Node 1: Encode Resume ====

def encode_resume(state):
    id = state["id"]
    dir_path = f"/mnt/uploads/images/{id}"

    image_files = [
        os.path.join(dir_path, f)
        for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]

    all_encoded_images = [encode_image(path) for path in image_files]
    return {**state, "all_encoded_images": all_encoded_images}

# ==== 5. Node 2: Evaluate Resume ====

def evaluate_candidate(state):
    jd = state["job_description"]
    images = state["all_encoded_images"]

    system_prompt = f"""
You are a hiring assistant.

Given the following resume and job description, analyze:

1. Is the candidate suitable for the role? (Yes/No + reason)
2. Key Strengths
3. Key Weaknesses
4. Suggested Improvements

Job Description:
{jd}
"""

    human_msg = HumanMessage(
        content=[
            {"type": "text", "text": "Here is the candidate's resume"},
            *[
                {"type": "image_url", "image_url": f"data:image/png;base64,{img}"}
                for img in images
            ]
        ]
    )

    response = llm.invoke([SystemMessage(content=system_prompt), human_msg])
    return {**state, "llm_result": response}


# ==== 6. Build LangGraph ====

builder = StateGraph(dict)
builder.add_node("encode_resume", encode_resume)
builder.add_node("evaluate_candidate", evaluate_candidate)

builder.set_entry_point("encode_resume")
builder.add_edge("encode_resume", "evaluate_candidate")
builder.set_finish_point("evaluate_candidate")

graph = builder.compile()




# ==== 7. Run Function ====

def run_resume_fit_analysis(id: str, job_description: str):

    result = graph.invoke({
        "id": id,
        "job_description": job_description,
    })

    return result

    print(f"Done JOB for id: {id}")
