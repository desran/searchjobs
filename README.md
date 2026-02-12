# Search & Apply Agents (A2A Protocol)

A multi-agent system built with the **A2A (Agent-to-Agent)** protocol and **Google ADK**. This project demonstrates how two independent agents can communicate and coordinate to perform a job search and application workflow.

## Architecture

The system consists of two primary components:

1.  **Search Agent** (`search_agent`):
    *   **Port**: 10001
    *   **Role**: Finds job listings for specific companies.
    *   **Tools**: `search_jobs` (web search via `ddgs`), `get_job_details`.
    *   **Output**: Stored as JSON files in `data/jobs/`.

2.  **Apply Agent** (`apply_agent`):
    *   **Port**: 10002
    *   **Role**: Processes applications for job listings found by the Search Agent.
    *   **Tools**: `apply_for_job` (simulates application).
    *   **Output**: Stored as text records in `data/resumes/`.

## Prerequisites

*   Python 3.10+ (Anaconda environment `searchjobs` is recommended).
*   Dependencies: `a2a-sdk` (installed from local source), `google-adk`, `ddgs`, `uvicorn`, `httpx`.

## Setup

1.  Activate your environment:
    ```powershell
    conda activate searchjobs
    ```

2.  Install dependencies:
    ```powershell
    pip install .
    # Or for development:
    pip install -e .
    ```

3.  Configure environment variables:
    *   Copy `.env.example` to `.env`:
        ```powershell
        cp .env.example .env
        ```
    *   Open `.env` and replace `your_api_key_here` with your actual **Google API Key**.

4.  Initialize data directories:
    ```powershell
    mkdir -p data/jobs data/resumes
    ```

## Usage

### Running the Agents

Start each agent in a separate terminal:

**Terminal 1 (Search Agent):**
```powershell
python -m search_agent
```

**Terminal 2 (Apply Agent):**
```powershell
python -m apply_agent
```

### Verification

### Automated Verification
You can run the end-to-end verification script to confirm everything is working:
```powershell
python verify_agents.py
```

### Manual Verification

1.  **Discovery Check**: Verify the agents are reachable by opening their Agent Card URLs in a browser:
    *   **Search Agent**: [http://127.0.0.1:10001/.well-known/agent-card.json](http://127.0.0.1:10001/.well-known/agent-card.json)
    *   **Apply Agent**: [http://127.0.0.1:10002/.well-known/agent-card.json](http://127.0.0.1:10002/.well-known/agent-card.json)

2.  **Functional Check (Search)**: Send a manual JSON-RPC request to the Search Agent:
    ```powershell
    curl.exe -X POST http://127.0.0.1:10001/ -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":"test","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Find jobs at Google"}],"messageId":"msg_123"}}}'
    ```

3.  **Data Verification**: Confirm that the Search Agent has extracted job listings:
    ```powershell
    dir data/jobs
    ```

4.  **Application Record**: Check if the Apply Agent has generated application documents:
    ```powershell
    dir data/resumes
    ```

## Configuration

*   **Host/Port**: Agents default to `127.0.0.1`. You can modify `DEFAULT_HOST` in each agent's `__main__.py`.
*   **LLM Capability**: By default, the executors use **Mock Logic** for verification (bypassing the need for an API key). To enable full ADK/Gemini reasoning:
    1.  Set `GOOGLE_API_KEY` in your environment.
    2.  Restore the `genai_parts` and `runner.run_async` logic in the `execute` methods of the executors.

## Project Structure

```text
## Agentic GUI (Web Interface)

A premium React-based dashboard is available for interacting with the agents visually.

### Running the GUI

1.  **Start the Backend Bridge**:
    ```powershell
    python bridge.py
    ```
    *The bridge runs on [http://127.0.0.1:8000](http://127.0.0.1:8000).*

2.  **Start the React Frontend**:
    ```powershell
    cd gui
    npm run dev
    ```
    *The frontend runs on [http://localhost:5173](http://localhost:5173).*

### Features
- **Smart Search**: Enter a company name to trigger the Search Agent via A2A.
- **Job Picker**: Select a job from the interactive results list.
- **Agent Apply**: Upload a resume (simulated) and apply for the selected job.
- **Protocol Logs**: View real-time status and A2A discovery metadata.
```


**# if you run into these errors ****


ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 10002): only
one usage of each socket address (protocol/network address/port) is normally permitted 

It means:
- You already have a server running on 127.0.0.1:10002, or
- A previous run didn’t shut down cleanly and the OS still considers the port “in use,” or
- Another application is using that port.


(searchjobs) C:\repos\searchjobs>python -m apply_agent
INFO:     Started server process [43192]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 10002): only one usage of each socket address (protocol/network address/port) is normally permitted
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.

**## Then do the following to kill the process:**

(searchjobs) C:\repos\searchjobs>netstat -ano | findstr :10002
  TCP    127.0.0.1:10002        0.0.0.0:0              LISTENING       34884

(searchjobs) C:\repos\searchjobs>taskkill /PID 34884 /F
SUCCESS: The process with PID 34884 has been terminated.

(searchjobs) C:\repos\searchjobs>python -m apply_agent
INFO:     Started server process [3944]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:10002 (Press CTRL+C to quit)
