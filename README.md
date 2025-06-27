# Candidate Screening RAG

## Description

**Resume Roaster RAG** is an asynchronous, queue-driven backend service that processes uploaded PDF resumes and job descriptions, converts resumes to images, and uses a Large Language Model (LLM) to analyze the candidate. The LLM evaluates if the candidate is the right fit for the job, and provides structured feedback on strengths, weaknesses, and areas for improvement—all based on the resume and job description provided by the user. The system is designed for scalability and modularity, leveraging FastAPI, MongoDB, Redis Queue, and Google Gemini LLM.

---

## Architecture

### 1. File Upload & Queueing
- The FastAPI server accepts PDF file uploads and a job description from the user.
- File metadata and job description are saved to MongoDB.
- The file is added to a processing queue (Redis Queue).

### 2. PDF Worker
- A worker process picks up the file from the queue.
- Converts the PDF to images (one per page).
- Updates the status in MongoDB.
- Adds a new job to the LLM queue.

### 3. LLM Worker
- Picks up the job from the LLM queue.
- Encodes the images to base64.
- Invokes the Google Gemini LLM with the images and the job description.
- The LLM returns a structured response:
  - **right_fit**: Whether the candidate is a good fit for the job.
  - **strengths**: List of candidate strengths.
  - **weaknesses**: List of candidate weaknesses.
  - **improvements**: Suggestions for improvement.
- Updates the MongoDB record with the LLM's analysis.

### 4. Status Endpoint
- Clients can query the `/status` endpoint with a file ID to get the current processing status and the LLM's structured analysis.

---

## Sample Input / Output

**Input:**  
- Upload a PDF resume and a job description via the `/upload` endpoint (as multipart form data).

**Output:**  
- Query `/status?id=<file_id>` to get:
    ```json
    {
      "file_id": "60f7c2e2e1b1a2b3c4d5e6f7",
      "file_name": "resume.pdf",
      "status": "handling by llm success",
      "response": {
        "right_fit": true,
        "strengths": ["Strong Python skills", "Team player"],
        "weaknesses": ["Limited leadership experience"],
        "improvements": ["Gain more project management experience"]
      }
    }
    ```

---

## Tech Stack

- **Python 3.12**
- **FastAPI** (API server)
- **MongoDB** (Async database)
- **Redis + RQ** (Queue management)
- **pdf2image** (PDF to image conversion)
- **Google Gemini LLM** (via LangChain)
- **Docker / Dev Containers** (for consistent development)
- **python-dotenv** (for environment variable management)

---

## How to Configure and Run

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd resume-roasting-rag
```

### 2. Set Up Environment Variables

Create an `.env` file in the `app/` directory with your Google API key:
```
GOOGLE_API_KEY=your-google-api-key
```

### 3. Start MongoDB and Redis

Ensure MongoDB and Redis are running (can be via Docker Compose or local services).

### 4. Install Python Dependencies

```sh
pip install -r requirements.txt
```

### 5. Run the FastAPI Server

```sh
sh run.sh
```

### 6. Start Worker Processes

In separate terminals, start the PDF and LLM workers (using RQ):

```sh
sh worker.sh
```

---

## Usage

- **Upload a PDF and job description** via the `/upload` endpoint (multipart form data).
- **Check status and results** via `/status?id=<file_id>`.

---

## Notes

- All uploads and generated images are stored in `/mnt/uploads/`.
- The project is designed for use in a dev container on Debian GNU/Linux 12.
- Make sure your `.env` and sensitive files are excluded