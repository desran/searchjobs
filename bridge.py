import os
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# A2A SDK imports
try:
    from a2a.client import ClientFactory
    from a2a.types import SendMessageRequest, Message, TextPart, MessageSendParams, SendMessageSuccessResponse
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from a2a.client import ClientFactory
    from a2a.types import SendMessageRequest, Message, TextPart, MessageSendParams, SendMessageSuccessResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEARCH_AGENT_URL = os.environ.get("SEARCH_AGENT_URL", "http://127.0.0.1:10001")
APPLY_AGENT_URL = os.environ.get("APPLY_AGENT_URL", "http://127.0.0.1:10002")

class SearchRequest(BaseModel):
    company: str

class ApplyRequest(BaseModel):
    job_id: str
    resume_name: str

@app.post("/search")
async def search_jobs(req: SearchRequest):
    print(f"WEB BRIDGE: Searching for jobs at {req.company} via {SEARCH_AGENT_URL}...")
    try:
        # Use ClientFactory.connect for automatic discovery and client creation
        a2a_client = await ClientFactory.connect(SEARCH_AGENT_URL)
        
        message = Message(
            role="user",
            parts=[TextPart(text=f"Find jobs at {req.company}")],
            message_id="web_search_" + os.urandom(4).hex()
        )
        
        # returns AsyncIterator[ClientEvent | Message]
        response_stream = a2a_client.send_message(message)
        
        result_text = ""
        async for update in response_stream:
            if isinstance(update, Message):
                for part in update.parts:
                    if hasattr(part.root, 'text'):
                        result_text += part.root.text
            else:
                task, _ = update
                if task.status == "completed" and task.artifacts:
                    result_text = ""
                    for art in task.artifacts:
                        for part in art.parts:
                            if hasattr(part.root, 'text'):
                                result_text += part.root.text
        
        if not result_text:
            print("WEB BRIDGE WARNING: No text results found in stream/task.")
            
        return {"status": "success", "result": result_text}
    except Exception as e:
        print(f"WEB BRIDGE EXCEPTION in /search: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apply")
async def apply_job(req: ApplyRequest):
    print(f"WEB BRIDGE: Applying for {req.job_id} using {req.resume_name} via {APPLY_AGENT_URL}...")
    try:
        a2a_client = await ClientFactory.connect(APPLY_AGENT_URL)
        
        message = Message(
            role="user",
            parts=[TextPart(text=f"Apply for job ID {req.job_id} using {req.resume_name}")],
            message_id="web_apply_" + os.urandom(4).hex()
        )
        
        response_stream = a2a_client.send_message(message)
        
        result_text = ""
        async for update in response_stream:
            if isinstance(update, Message):
                for part in update.parts:
                    if hasattr(part.root, 'text'):
                        result_text += part.root.text
            else:
                task, _ = update
                if task.status == "completed" and task.artifacts:
                    result_text = ""
                    for art in task.artifacts:
                        for part in art.parts:
                            if hasattr(part.root, 'text'):
                                result_text += part.root.text
                            
        return {"status": "success", "result": result_text}
    except Exception as e:
        print(f"WEB BRIDGE EXCEPTION in /apply: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def list_jobs():
    jobs_dir = "data/jobs"
    if not os.path.exists(jobs_dir):
        return []
    import json
    files = [f for f in os.listdir(jobs_dir) if f.endswith(".json")]
    jobs = []
    for f in files:
        try:
            with open(os.path.join(jobs_dir, f), 'r') as jf:
                jobs.append(json.load(jf))
        except:
            continue
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
