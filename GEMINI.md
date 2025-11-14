# Project: AI Cluster Orchestrator

**CURRENT TASK: Docker Setup**
> We are currently in the process of setting up Docker to containerize the AI server.
> For a detailed plan and our current progress, please see [DOCKER_SETUP.md](./DOCKER_SETUP.md).

## Project Overview

This project, `ai_cluster_orchestrator`, aims to create a distributed AI agent system. It allows a powerful central machine ("Titan") to orchestrate Large Language Model (LLM) tasks, delegating specialized functions to less powerful machines ("Iron Chef", "ArtforgeOG") across a local network. The system integrates web search capabilities and local file system access (via the client) to provide context-aware and tool-augmented responses.

The core idea is to leverage the strengths of multiple machines:
*   **Titan:** Acts as the primary orchestrator and runs the most powerful LLM (e.g., Yi-34B).
*   **Iron Chef:** Runs a capable specialist LLM for general reasoning or specific tasks.
*   **ArtforgeOG:** Runs a fast, lightweight LLM for utility tasks like data extraction or simple summarization.

## Main Technologies

*   **Language:** Python 3.x
*   **Web Framework:** FastAPI (for the server API)
*   **ASGI Server:** Uvicorn (to run the FastAPI application)
*   **HTTP Client:** `requests` (for making API calls and between services)
*   **Environment Management:** `python-dotenv` (for loading configuration from `.env` files)
*   **Web Search:** `googlesearch-python` (for performing web searches)
*   **LLM Runtime:** Ollama (for running local open-source LLMs)

## Architecture

The system follows a client-server model with a central orchestrator:

1.  **CLI Client (on "Merlin"):** A command-line interface on the user's primary machine ("Merlin") sends prompts to the FastAPI server.
2.  **FastAPI Server (on "Titan"):** This is the orchestrator. It receives prompts, decides on a course of action (e.g., perform a web search, call a local LLM, instruct the client to perform a local tool call), and manages the flow of information.
3.  **Local LLM  Instances (on "Titan", "Iron Chef", "ArtforgeOG"):** Each machine in the cluster runs its own Local LLM instance, hosting an LLM tailored to its hardware capabilities and intended role. The FastAPI server communicates with these instances via their respective APIs.
4.  **Tool Calls:** The orchestrator can instruct the CLI client to perform local actions (e.g., `read_file`, `write_file`) on "Merlin's" filesystem. It can also perform web searches directly.

## Building and Running

### Dependencies

Dependencies are managed using `requirements.txt`.

### Setup

1.  **LLM Installation:** Ensure LLM is installed and running on "Titan" (and potentially "Iron Chef", "ArtforgeOG") with the appropriate models pulled (e.g., `ollama run yi:34b` on Titan).
2.  **Virtual Environment:** Navigate to the project root (`ai_cluster_orchestrator`) and create a Python virtual environment:
    ```bash
    python3 -m venv .venv
    ```
3.  **Activate Environment:** Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4.  **Install Dependencies:** Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Environment Configuration:** Create a `.env` file in the project root based on `.env.example`. Populate it with the correct `_HOST` (e.g., `http://localhost:11434` for Titan) and `OLLAMA_MODEL` (e.g., `yi:34b`).

### Running the Server

1.  Ensure your virtual environment is activated.
2.  From the project root (`ai_cluster_orchestrator`), execute the following command:
    ```bash
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```
    This will start the FastAPI server, making it accessible on your local network.

## Development Conventions

*   **Language:** Python 3.x
*   **Frameworks:** FastAPI for the server.
*   **Configuration:** Environment variables loaded via `python-dotenv` from a `.env` file.
*   **Project Structure:**
    *   `src/`: Contains the FastAPI server application logic.
    *   `client/`: Will contain the CLI client application.
*   **Tooling:** `pip` for package management, `uvicorn` for serving the API.

## AI Cluster Hardware & Roles

This section documents the hardware specifications and recommended model classes for each machine in the AI cluster.

### Titan (Orchestrator)
*   **Machine:** Alienware Aurora R16
*   **Role:** Primary orchestrator, handling complex reasoning and agent coordination.
*   **CPU:** Intel(R) Core(TM) i9-14900F
*   **RAM:** 32GB DDR5
*   **GPU:** NVIDIA(R) GeForce RTX(TM) 4080 SUPER
*   **VRAM:** 16GB GDDR6X
*   **Recommended Model Class:** 34B Parameter Models (e.g., Yi-1.5 34B, Command R 35B).

### Iron Chef (Specialist)
*   **Machine:** Custom Build (MSI Z270-A Pro)
*   **Role:** General reasoning, summarization, and other specialized tasks.
*   **CPU:** Intel(R) Core(TM) i5-7600K
*   **RAM:** 32GB DDR4
*   **GPU:** GeForce(R) GTX 1070
*   **VRAM:** 8GB GDDR5
*   **Recommended Model Class:** 7-8B Parameter Models (e.g., Qwen2-7B, Llama-3-8B).

### ArtforgeOG (Utility)
*   **Machine:** Dell XPS 15 9570
*   **Role:** Fast, lightweight tasks like data extraction, formatting, and simple classifications.
*   **CPU:** Intel(R) Core(TM) i7-8750H
*   **RAM:** 16GB DDR4
*   **GPU:** NVIDIA(R) GeForce GTX 1050Ti
*   **VRAM:** 4GB
*   **Recommended Model Class:** 1.5-3B Parameter Models (e.g., Qwen2-1.5B, Gemma 2B, Phi-3-mini).
