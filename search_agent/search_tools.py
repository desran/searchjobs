import json
import os
from ddgs import DDGS

JOBS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'jobs')
os.makedirs(JOBS_DIR, exist_ok=True)

def search_jobs(company_name: str) -> str:
    """Searches for jobs for a given company using DuckDuckGo and saves them locally.

    Args:
        company_name: The name of the company to search jobs for.

    Returns:
        A JSON string containing the list of found jobs.
    """
    print(f"Searching for jobs at {company_name}...")
    results = []
    try:
        with DDGS() as ddgs:
            # simple search query
            query = f"{company_name} careers jobs"
            # We can use 'text' search or 'news', let's stick to text for simplicity
            # or try to find a more specific way if DDGS supports it. 
            # DDGS has 'text', 'images', 'videos', 'news', 'maps', 'translate', 'suggestions'.
            # It doesn't have a specific 'jobs' search method publicly documented as stable/common in all versions, 
            # but let's assume standard text search is good enough to find *links* to jobs.
            
            # Actually, let's try to extract something reasonable.
            search_results = list(ddgs.text(query, max_results=10))
            print(f"DDGS returned {len(search_results)} results.")
            
            if not search_results:
                print("No results found or error in retrieval. Using MOCK data.")
                # Fallback to mock data for demonstration
                search_results = [
                    {'title': f'{company_name} Software Engineer', 'body': 'Job description placeholder...', 'href': 'http://example.com/job1'},
                    {'title': f'{company_name} Data Scientist', 'body': 'Job description placeholder...', 'href': 'http://example.com/job2'},
                ]
                
            for i, res in enumerate(search_results):
                job_id = f"{company_name.lower().replace(' ', '_')}_{i}"
                job = {
                    "id": job_id,
                    "title": res.get("title"),
                    "company": company_name,
                    "description": res.get("body"),
                    "url": res.get("href")
                }
                results.append(job)
                
                # Save to file
                job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
                with open(job_file, "w") as f:
                    json.dump(job, f, indent=2)
                    
    except Exception as e:
        return f"Error searching for jobs: {e}"

    return json.dumps(results, indent=2)

def get_job_details(job_id: str) -> str:
    """Retrieves details for a specific job ID from local storage.

    Args:
        job_id: The ID of the job to retrieve.

    Returns:
        JSON string of the job details or an error message.
    """
    job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
    if os.path.exists(job_file):
        with open(job_file, "r") as f:
            return f.read()
    return f"Job with ID {job_id} not found."
