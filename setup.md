### AI Cluster Setup Checklist

This guide will walk you through setting up your distributed AI cluster, from hardware preparation to running your first prompt.

---

### ☐ 1. Hardware & Operating System Setup

-   [ ] **Titan:** Install your ArchLinux "Omarchy" build on the spare 1TB drive.
-   [ ] **Iron Chef:** Install your ArchLinux "Omarchy" build.
-   [ ] **ArtforgeOG:** Ensure the operating system is installed and ready.
-   [ ] **Merlin:** Ensure your primary machine is ready.

---

### ☐ 2. Physical Network Configuration

-   [ ] **Acquire Ethernet Cables:** You will need at least four Ethernet cables, one for each computer (Merlin, Titan, Iron Chef, ArtforgeOG).
-   [ ] **Connect to Router/Switch:**
    -   Plug one end of an Ethernet cable into the network port of each computer.
    -   Plug the other end of each cable into an available LAN port on your network router or switch.
-   [ ] **Verify Network Connectivity & IP Addresses:**
    -   Once all machines are booted and connected, verify they have received an IP address from your router. You can typically find this by running `ip addr` or `ifconfig` in the terminal on each Linux machine.
    -   **Recommendation:** For a stable setup, configure your router to assign a *static IP address* to Titan, Iron Chef, and ArtforgeOG. This prevents their addresses from changing, which would break the API connections. Note these IP addresses for the software setup step.

---

### ☐ 3. Ollama & LLM Model Installation

On each machine, you will need to install Ollama and then pull the specific model designated for it.

-   [ ] **Install Ollama:**
    -   On Titan, Iron Chef, and ArtforgeOG, follow the official Ollama instructions for Linux: `curl -fsSL https://ollama.com/install.sh | sh`
-   [ ] **Pull LLM Models:**
    -   **On Titan:** Open a terminal and run:
        ```bash
        ollama run yi:34b
        ```
    -   **On Iron Chef:** Open a terminal and run:
        ```bash
        ollama run llama3:8b
        ```
    -   **On ArtforgeOG:** Open a terminal and run:
        ```bash
        ollama run phi3:mini
        ```
    *(Note: The first run will download the model, which may take some time.)*

---

### ☐ 4. Orchestrator Server Setup (on Titan)

This step configures the central FastAPI server that manages the cluster.

-   [ ] **Clone Project:** Place the `ai_cluster_orchestrator` project directory onto Titan.
-   [ ] **Set Up Python Environment:**
    ```bash
    # Navigate to the project directory
    cd ai_cluster_orchestrator

    # Create and activate a virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```
-   [ ] **Configure Environment Variables:**
    -   Create a `.env` file by copying the example: `cp .env.example .env`
    -   Edit the `.env` file. This is the most critical step for networking the cluster. You will need to define the addresses for each specialist LLM. It should look something like this, replacing the example IPs with the actual static IP addresses you noted earlier:

        ```env
        # .env on Titan
        OLLAMA_HOST=http://localhost:11434
        OLLAMA_MODEL=yi:34b

        # Endpoints for the other models in the cluster
        IRON_CHEF_URL=http://<IP_OF_IRON_CHEF>:11434
        ARTFORGE_OG_URL=http://<IP_OF_ARTFORGE_OG>:11434
        ```
-   [ ] **Run the Orchestrator Server:**
    ```bash
    # Make sure your virtual environment is still active
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```
    The `--host 0.0.0.0` flag makes the server accessible to other machines on your local network, not just on Titan itself.

---

### ☐ 5. Client Operation (on Merlin)

Finally, run prompts from your primary machine, Merlin.

-   [ ] **Ensure Client is Ready:** The `client/cli.py` file should be on your Merlin machine within the project structure.
-   [ ] **Run a Prompt:**
    -   Open a terminal on Merlin.
    -   Execute the client script, pointing it to Titan's IP address and providing your prompt. The exact command will depend on the `cli.py` implementation, but it will look similar to this:
        ```bash
        python /path/to/ai_cluster_orchestrator/client/cli.py --host http://<IP_OF_TITAN>:8000 --prompt "Your request here"
        ```
    -   The orchestrator on Titan will receive the request, delegate tasks to the other machines as needed, and stream the final response back to your terminal on Merlin.