import logging
import os
import sys

# Add the parent directory to sys.path
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
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, TextPart
from google.genai import types

# Reuse simplified executor logic (ideally this should be shared or imported)
from a2a.server.agent_execution import AgentExecutor

# Copying simplified executor for standalone capability
class ApplyAgentExecutor(AgentExecutor):
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
        
        print(f"Executing Apply Agent with message: {text}")
        
        if "apply" in text.lower():
            # Mock extraction of job_id
            import re
            match = re.search(r"ID (\S+)", text)
            job_id = match.group(1) if match else "unknown"
            
            from .apply_tools import apply_for_job
            # In a real scenario, it would call Search Agent here if details missing
            # For this mock, we just call the tool with dummy details/content
            result = apply_for_job(job_id, "Mock Job Details", "Mock Resume Content")
            response_text = f"Application request processed for job {job_id}. Status: {result}"
        else:
            response_text = f"I received your message: {text}. I am an Apply Agent."

        response_parts = [TextPart(text=response_text)]
        await updater.add_artifact(response_parts)
        await updater.update_status(TaskState.completed, final=True)

    async def cancel(self, context, event_queue):
        pass

from .agent import create_apply_agent

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 10002 # Apply Agent on 10002

def main():
    agent = create_apply_agent()
    
    # Use localhost for the public URL, but bind to 0.0.0.0
    app_url = os.environ.get('APPLY_AGENT_URL', f'http://localhost:{DEFAULT_PORT}')
    
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id='apply_job_skill',
        name='Apply Job',
        description='Applies for a job given an ID and resume',
        tags=['apply', 'jobs'],
        examples=['Apply for job google_0 with my_resume.txt'],
    )
    
    agent_card = AgentCard(
        name='Apply Agent',
        description='Agent that applies for jobs',
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
    
    executor = ApplyAgentExecutor(runner, agent_card)
    handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
    
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
    
    uvicorn.run(app.build(), host=DEFAULT_HOST, port=DEFAULT_PORT)

if __name__ == '__main__':
    main()
