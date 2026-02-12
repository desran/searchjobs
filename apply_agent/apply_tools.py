import os
import json
import httpx
import uuid
import asyncio # needed if we were running async in tools, but standard tools are sync or async. 
# ADK tools can be async.

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import SendMessageRequest, MessageSendParams, SendMessageSuccessResponse, Task

SEARCH_AGENT_URL = os.environ.get('SEARCH_AGENT_URL', 'http://localhost:10001')
RESUMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resumes')
os.makedirs(RESUMES_DIR, exist_ok=True)

async def get_job_details_from_search_agent(job_id: str) -> str:
    """Retrieves job details from the Search Agent using A2A.

    Args:
        job_id: The ID of the job to retrieve.

    Returns:
        The job details or an error message.
    """
    print(f"Connecting to Search Agent at {SEARCH_AGENT_URL} for job {job_id}...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resolver = A2ACardResolver(client, SEARCH_AGENT_URL)
            card = await resolver.get_agent_card()
            
            agent_client = A2AClient(client, card, url=SEARCH_AGENT_URL)
            
            message_id = uuid.uuid4().hex
            payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': f'Get details for job ID: {job_id}'}],
                    'messageId': message_id,
                }
            }
            
            request = SendMessageRequest(id=message_id, params=MessageSendParams.model_validate(payload))
            response = await agent_client.send_message(request)
            
            if isinstance(response.root, SendMessageSuccessResponse):
                 result = response.root.result
                 # Result is a Task object. We need to extract the "output" or last message.
                 # The 'Task' object in a2a-sdk might have changed or I need to check its structure.
                 # Based on 'host_agent_executor.py', the response is a list of parts in the task update.
                 # But 'send_message' returns a 'Task' object which represents the task state.
                 # We usually look at 'task.status' and 'task.artifacts' or messages.
                 
                 # Let's simple return the whole task rep for now or try to find the text.
                 # If the task is completed, we should find the answer.
                 return str(result) 
            else:
                return f"Error from Search Agent: {response}"
                
    except Exception as e:
        return f"Failed to communicate with Search Agent: {e}"

def read_resume(resume_filename: str) -> str:
    """Reads a resume file from the local resumes directory.

    Args:
        resume_filename: The name of the resume file.

    Returns:
        The content of the resume.
    """
    resume_path = os.path.join(RESUMES_DIR, resume_filename)
    if os.path.exists(resume_path):
        with open(resume_path, "r") as f:
            return f.read()
    return f"Resume file {resume_filename} not found."

def apply_for_job(job_id: str, job_details: str, resume_content: str) -> str:
    """Simulates applying for a job.

    Args:
        job_id: The job ID.
        job_details: The job details string.
        resume_content: The resume content.

    Returns:
        Status message.
    """
    print(f"Applying for job {job_id}...")
    # Mock application logic
    application_file = os.path.join(RESUMES_DIR, f"application_{job_id}.txt")
    with open(application_file, "w") as f:
        f.write(f"Application for Job {job_id}\n")
        f.write(f"Details: {job_details}\n")
        f.write(f"Resume: {resume_content}\n")
        
    return f"Successfully applied for Job {job_id}. Application saved to {application_file}."
