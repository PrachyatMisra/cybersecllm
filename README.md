# CybersecLLM

<br/>
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Neo4j-018bff?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama" />
</div>
<br/>

**CybersecLLM** is a comprehensive Cybersecurity Knowledge Graph and Threat Intelligence platform. It utilizes local Natural Language Processing (via Ollama) and a Neo4j Graph Database to autonomously ingest, correlate, and visualize structured and unstructured cybersecurity intel.

Architected and developed by **Prachyat Misra**, this project demonstrates how modern graph databases and local LLMs can be orchestrated to model complex threat landscapes, providing interactive analytics and automated entity extraction without relying on external APIs.

## ✨ Core Capabilities

- **Automated Data Ingestion:** Import cyber intelligence from versatile sources into a unified Neo4j schema:
  - **MITRE ATT&CK STIX Parsing:** Direct mapping of Tactics, Techniques, and Malware from the official MITRE STIX JSON distribution.
  - **YouTube Transcript Processing:** AI-powered extraction of threat contexts from cybersecurity conference talks and briefings.
  - **PDF Threat Report Parsing:** Automated extraction of CVEs, Threat Actors, and network indicators directly from local threat advisories (e.g., Mandiant, CISA reports).
- **RAG Analytics Engine:** (Retrieval-Augmented Generation) A hybrid vector and graph traversal querying system utilizing a local *Llama3* instance. It interacts securely with the ingested knowledge base, ensuring sensitive data remains on-premise.
- **Attack Path Emulation:** Native Neo4j shortest-path analytics to identify and map the shortest operational chains between threat entry points and critical assets.
- **Interactive 3D Graph Visualization:** A hardware-accelerated force-directed graph (Three.js/D3) rendered natively in the browser. Features include dynamic node rendering, physics-based repulsion, and an inspection pane exposing LLM-reasoning traces.

## 🚀 Getting Started

The platform runs entirely locally and uses Docker for simplified dependency management.

### Prerequisites

- Docker Desktop / Docker Compose
- Python 3.9+
- Ollama (installed locally)
- Llama3 Model (`ollama pull llama3`)

### Installation & Launch

Boot the entire infrastructure with the included setup sequence:

```bash
git clone https://github.com/prachyatmisra/cybersecllm.git
cd cybersecllm

# Make the setup script executable and run it
chmod +x setup.sh
./setup.sh
```

The script will:
1. Ensure Ollama models are pulled.
2. Install Python dependencies in the virtual environment.
3. Spin up the Neo4j Docker container.
4. Launch the Streamlit application interface.

Access the platform at `http://localhost:8505` (or whichever port Streamlit binds to).

## 🛠 Architecture

CybersecLLM operates on a robust, entirely local tech stack:
- **Frontend / UI:** Streamlit (Python) leveraging custom components to render `Three.js` and `3d-force-graph` data dynamically.
- **Data Layer:** Neo4j Community Server handled via the official `neo4j` Python driver.
- **LLM Pipeline:** Langchain bindings managing execution logic with local `Ollama` sockets.

## 📄 Licensing

This project is licensed under the MIT License.

---
*Developed by Prachyat Misra.*
