import logging
import os
import sys

# Add the parent directory to sys.path to allow imports from sibling directories if needed
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from google.adk import Runner
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

# For HostAgentExecutor (we can reuse the logic from samples, or define a simple one)
# Since I cannot easily import HostAgentExecutor from the samples without copying, 
# and A2A SDK doesn't seem to export a generic "AdkAgentExecutor" yet (based on my reading),
# I should probably define a simple Executor here or copy `HostAgentExecutor` logic.
# However, `a2a.server.agent_execution.AgentExecutor` is abstract.
# Let's see if I can use a default implementation or if I need to implement it.
# The sample used `HostAgentExecutor` which inherits from `AgentExecutor`.
# I will implement a simple `SearchAgentExecutor` here based on `HostAgentExecutor`.

from a2a.server.agent_execution import AgentExecutor
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, TextPart
from google.genai import types

class SearchAgentExecutor(AgentExecutor):
    def __init__(self, runner: Runner, card: AgentCard):
        self.runner = runner
        self._card = card

    async def execute(self, context, event_queue, response_trace=None):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)

        # Simplified logic: bypass LLM for verification
        text = ""
        for part in context.message.parts:
            if part.root.kind == 'text':
                text += part.root.text
        
        print(f"Executing Search Agent with message: {text}")
        
        if "find jobs" in text.lower() or "search" in text.lower():
            # Mock extraction: search for company name
            words = text.split()
            company = words[-1] if words else "Google"
            from .search_tools import search_jobs
            results_json = search_jobs(company)
            import json
            results = json.loads(results_json)
            response_text = f"I searched for jobs at {company} and found {len(results)} results."
        elif "get job details" in text.lower() or "job id" in text.lower():
            words = text.split()
            job_id = words[-1]
            from .search_tools import get_job_details
            details = get_job_details(job_id)
            response_text = f"Details for job {job_id}: {details}"
        else:
            response_text = f"I received your message: {text}. I am a Search Agent and I can find jobs for you."

        response_parts = [TextPart(text=response_text)]
        await updater.add_artifact(response_parts)
        await updater.update_status(TaskState.completed, final=True)
            # Handle intermediate steps/updates if necessary

    async def cancel(self, context, event_queue):
        pass # simple implementation

from .agent import create_search_agent

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 10001 # Search Agent on 10001 (Apply on 10002)

def main():
    agent = create_search_agent()
    
    # Use localhost for the public URL, but bind to 0.0.0.0
    app_url = os.environ.get('SEARCH_AGENT_URL', f'http://localhost:{DEFAULT_PORT}')
    
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id='search_jobs_skill',
        name='Search Jobs',
        description='Searches for jobs by company name',
        tags=['search', 'jobs'],
        examples=['Find jobs at Google'],
    )
    
    agent_card = AgentCard(
        name='Search Agent',
        description='Agent that searches for jobs',
        url=app_url,
        version='0.1.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[skill],
    )
    
    runner = Runner(
        app_name=agent_card.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    executor = SearchAgentExecutor(runner, agent_card)
    handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
    
    # Create A2A application
    a2a_app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
    app = a2a_app.build()
    
    # Run server
    uvicorn.run(app, host=DEFAULT_HOST, port=DEFAULT_PORT)

if __name__ == '__main__':
    main()
