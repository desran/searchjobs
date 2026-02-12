from google.adk import Agent
from .search_tools import search_jobs, get_job_details

def create_search_agent() -> Agent:
    """Creates the Search Agent instance."""
    
    agent = Agent(
        model='gemini-2.5-flash-lite', # Using a lightweight model
        name='Search_Agent',
        instruction="""
        You are a Search Agent. Your goal is to find job listings for specific companies.
        You have access to a tool `search_jobs` which takes a company name and returns a list of jobs found on the web.
        You also have `get_job_details` to retrieve stored job information relative to a job ID.
        
        When asked to find jobs for a company, use `search_jobs`.
        When asked about a specific job ID, use `get_job_details`.
        
        Always return the information you find clearly.
        """,
        tools=[search_jobs, get_job_details],
    )
    return agent
