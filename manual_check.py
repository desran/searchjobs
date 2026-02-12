import httpx
import asyncio
import sys

async def check_agent(url):
    print(f"Checking {url}...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{url}")
            print(f"Status: {resp.status_code}")
            print(f"Content: {resp.text[:200]}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")

async def main():
    # Attempt to check both agents assumed to be running if verification script left them running (unlikely as it terminates them)
    # So this script is useless unless I start the agents manually first.
    pass

if __name__ == "__main__":
    # Ensure this runs only if servers are up. 
    # But I can use this script to verify while running agents in another process.
    # For now, I'll just put the check logic.
    if len(sys.argv) > 1:
        url = sys.argv[1]
        asyncio.run(check_agent(url))
    else:
        print("Usage: python manual_check.py <url>")
