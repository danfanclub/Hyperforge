# Docker Setup Plan for Hyperforge

This document outlines the plan and progress for containerizing the `ai_cluster_orchestrator` application using Docker.

## Goal

The primary goal is to create a portable, scalable, and easy-to-manage environment for the AI orchestrator server. This will allow the server to run in the background and be easily deployed to multiple machines in the future.

## Plan & Progress

1.  **[Completed] Decide to use Docker:** We decided that Docker is the best approach for this project, offering portability, simplified startup, and scalability.

2.  **[Completed] Create `Dockerfile`:** A `Dockerfile` has been created in the `Hyperforge` directory. This file defines the environment for the server, including the Python version, dependencies, and startup command.

3.  **[Completed] Create `docker-compose.yml`:** A `docker-compose.yml` file has been created. This file defines the `ai-orchestrator` service, how to build it, which ports to expose, and how to pass environment variables.

4.  **[Completed] Configure `.env` file:** The `ai_cluster_orchestrator/.env` file has been created and configured with `OLLAMA_HOST=http://host.docker.internal:11434` to allow the Docker container to communicate with the Ollama instance on the host machine.

5.  **[In Progress] Install and Configure Docker:**
    *   **[Completed]** Docker has been installed using `pacman`.
    *   **[Completed]** `docker-compose` has been installed using `pacman`.
    *   **[Completed]** The Docker service has been started and enabled to start on boot.
    *   **[Completed]** The current user (`merlin`) has been added to the `docker` group.

6.  **[Next Step] Log Out and Log Back In:** To apply the group membership changes, the user needs to log out of their current session and log back in.

7.  **[Pending] Push Docker files to GitHub:** After logging back in, run `git push` from the `/home/merlin/Documents/Hyperforge` directory to push the new Docker-related files to the GitHub repository.

8.  **[Pending] Build and Run the Docker Container:** After pushing the files, the next step is to run `docker-compose up --build -d` from the `/home/merlin/Documents/Hyperforge` directory to build the Docker image and start the server container in the background.

9.  **[Pending] Create a `hyperforge` Client Script:** Once the server is running in Docker, we will create a simple, native `hyperforge` script that can be run from any directory to interact with the AI server.

10. **[Pending] Move the `hyperforge` script to a `bin` directory:** To make the `hyperforge` command globally accessible.
