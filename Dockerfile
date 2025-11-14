# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# Note: We copy only the requirements file first to leverage Docker's layer caching.
# This way, dependencies are only re-installed if requirements.txt changes.
COPY ./ai_cluster_orchestrator/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY ./ai_cluster_orchestrator/ /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run uvicorn when the container launches
# The command is specified in a list to be a JSON array, which is the preferred format.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
