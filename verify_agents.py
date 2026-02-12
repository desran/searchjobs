import subprocess
import time
import os
import sys
import requests
import json
import httpx
import asyncio
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, SendMessageRequest, MessageSendParams, SendMessageSuccessResponse

# Set environment
env = os.environ.copy()
env['PYTHONPATH'] = os.getcwd()

# Helper to send message
async def send_message_to_agent(agent_url, text):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First check if card is accessible
            card_url = f"{agent_url.rstrip('/')}/.well-known/agent-card.json"
            print(f"Checking card at {card_url}...")
            card_resp = await client.get(card_url)
            if card_resp.status_code != 200:
                print(f"Card not found at {card_url}: {card_resp.status_code}")
                # Try fallback
                card_url = f"{agent_url.rstrip('/')}/.well-known/agent.json"
                print(f"Checking fallback card at {card_url}...")
                card_resp = await client.get(card_url)
            
            if card_resp.status_code == 200:
                print(f"Card found at {card_url}")
                card_data = card_resp.json()
                card = AgentCard.model_validate(card_data)
                agent_client = A2AClient(client, card, url=agent_url)
            else:
                print(f"Failed to find card at any standard path. Using resolver as last resort.")
                resolver = A2ACardResolver(client, agent_url)
                card = await resolver.get_agent_card()
                agent_client = A2AClient(client, card, url=agent_url)
            
            message_id = "test_" + str(time.time())
            payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': text}],
                    'messageId': message_id,
                }
            }
            request = SendMessageRequest(id=message_id, params=MessageSendParams.model_validate(payload))
            response = await agent_client.send_message(request)
            return response
    except Exception as e:
        print(f"Error sending message to {agent_url}: {e}")
        with open("connection_error.log", "a") as f:
            f.write(f"Error connecting to {agent_url}: {e}\n")
        return None

async def main():
    print("Starting Search Agent...")
    search_out_f = open("search_stdout.log", "w")
    search_err_f = open("search_stderr.log", "w")
    search_process = subprocess.Popen(
        [sys.executable, "-m", "search_agent"],
        env=env,
        cwd=os.getcwd(),
        stdout=search_out_f,
        stderr=search_err_f
    )
    
    print("Starting Apply Agent...")
    apply_out_f = open("apply_stdout.log", "w")
    apply_err_f = open("apply_stderr.log", "w")
    apply_process = subprocess.Popen(
        [sys.executable, "-m", "apply_agent"],
        env=env,
        cwd=os.getcwd(),
        stdout=apply_out_f,
        stderr=apply_err_f
    )
    
    try:
        print("Waiting for agents to start (30s)...")
        await asyncio.sleep(30)
        
        # Test Search Agent
        print("\n--- Testing Search Agent ---")
        response = await send_message_to_agent("http://127.0.0.1:10001", "Find jobs at Google")
        if response:
            print("Search Agent Response Received")
            # Verify jobs created
            await asyncio.sleep(5)
            jobs_dir = "data/jobs"
            files = os.listdir(jobs_dir) if os.path.exists(jobs_dir) else []
            print(f"Jobs found in {jobs_dir}: {len(files)}")
            if len(files) > 0:
                print("SUCCESS: Search Agent created job files.")
                job_id = files[0].replace(".json", "")
                print(f"Using Job ID: {job_id}")
                
                # Test Apply Agent
                print("\n--- Testing Apply Agent ---")
                apply_msg = f"Apply for job ID {job_id} using resume my_resume.txt"
                apply_response = await send_message_to_agent("http://127.0.0.1:10002", apply_msg)
                
                if apply_response:
                    print("Apply Agent Response Received")
                    # Verify application created
                    await asyncio.sleep(5)
                    app_file = f"data/resumes/application_{job_id}.txt"
                    if os.path.exists(app_file):
                        print(f"SUCCESS: Application file {app_file} created.")
                    else:
                        print(f"FAILURE: Application file {app_file} NOT found.")
                else:
                    print("FAILURE: Apply Agent did not respond.")
            else:
                print("FAILURE: Search Agent did not create job files.")
        else:
            print("FAILURE: Search Agent did not respond.")
            
    finally:
        print("\nStopping agents...")
        search_process.terminate()
        apply_process.terminate()
        
        try:
            search_process.wait(timeout=5)
            apply_process.wait(timeout=5)
        except:
             pass
        
        search_out_f.close()
        search_err_f.close()
        apply_out_f.close()
        apply_err_f.close()
        
        # Merge logs into verification_result.log
        with open("verification_result.log", "w", encoding="utf-8") as f:
            f.write("--- Search Agent Output ---\n")
            with open("search_stdout.log", "r") as src: f.write(src.read())
            f.write("\n--- Search Agent Error ---\n")
            with open("search_stderr.log", "r") as src: f.write(src.read())
            f.write("\n--- Apply Agent Output ---\n")
            with open("apply_stdout.log", "r") as src: f.write(src.read())
            f.write("\n--- Apply Agent Error ---\n")
            with open("apply_stderr.log", "r") as src: f.write(src.read())
                
        print("Logs written to verification_result.log")

if __name__ == '__main__':
    asyncio.run(main())
