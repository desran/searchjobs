from google.adk import Agent
from .apply_tools import get_job_details_from_search_agent, read_resume, apply_for_job

def create_apply_agent() -> Agent:
    """Creates the Apply Agent instance."""
    
    agent = Agent(
        model='gemini-2.5-flash-lite',
        name='Apply_Agent',
        instruction="""
        You are an Apply Agent. Your goal is to apply for jobs.
        To apply for a job, you typically need a Job ID and a resume filename.
        
        Follow these steps:
        1. If you have a Job ID, first verify it and get details using `get_job_details_from_search_agent`.
        2. Read the specified resume using `read_resume`.
        3. Once you have the details and the resume, use `apply_for_job`.
        
        If you are missing information (like resume filename), ask the user.
        """,
        tools=[get_job_details_from_search_agent, read_resume, apply_for_job],
    )
    return agent
