# AI Cluster LLM Model Recommendations

This document outlines the recommended Large Language Models (LLMs) for each machine in the AI cluster, based on their hardware specifications and intended roles.

## Titan (Orchestrator)

*   **Role:** Primary orchestrator, handling complex reasoning, agent coordination, and novel writing.
*   **Hardware:** NVIDIA GeForce RTX 4080 SUPER (16GB VRAM)
*   **Front-Runner Model:** `gpt-oss-20B`
*   **Reasoning:** Despite its "20B" name, this is an OpenAI-developed Mixture-of-Experts (MoE) model that activates only 3.6 billion parameters per pass. This makes it incredibly fast and efficient on Titan's 16GB VRAM, leaving ample headroom for large context windows. Its strong reasoning, instruction following, and agentic capabilities, combined with OpenAI's quality, make it an ideal partner for creative writing and complex orchestration tasks.

## Iron Chef (Specialist)

*   **Role:** General reasoning, summarization, and other specialized tasks.
*   **Hardware:** GeForce GTX 1070 (8GB VRAM)
*   **Front-Runner Model:** `Qwen2 8B`
*   **Reasoning:** The 8B parameter class is the sweet spot for Iron Chef's 8GB VRAM. Qwen2 8B is a top-tier model known for its strong performance, making it an excellent choice for a capable specialist LLM that can handle nuanced tasks efficiently.

## ArtforgeOG (Utility)

*   **Role:** Fast, lightweight tasks like data extraction, formatting, and simple classifications.
*   **Hardware:** NVIDIA GeForce GTX 1050Ti (4GB VRAM)
*   **Front-Runner Model:** `Phi-3-mini`
*   **Reasoning:** Phi-3-mini (3.8B parameters) is renowned for its exceptional performance relative to its small size. It will run efficiently on ArtforgeOG's 4GB VRAM, providing quick and capable responses for utility tasks without requiring significant resources.