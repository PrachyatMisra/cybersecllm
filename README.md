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

**CybersecLLM** is an advanced, industry-grade Threat Intelligence Platform and Knowledge Graph Intelligence System. It leverages state-of-the-art Natural Language Processing (via local Ollama inference) and a Neo4j Graph Database to autonomously ingest, correlate, and visualize complex cybersecurity threats.

Built from scratch by **Prachyat Misra**, this platform is designed to provide security analysts with real-time, interactive graph analytics, offering a cohesive single-pane-of-glass into an organization's threat landscape.

## ✨ Features

- **Automated Data Ingestion Protocol:** Seamlessly import cyber intelligence from multiple unstructured and structured domains:
  - **MITRE ATT&CK STIX Parsing:** Direct integration with MITRE matrix distributions to map Tactics, Techniques, and Malware.
  - **YouTube Transcript Processing:** AI-powered extraction of threat contexts from cybersecurity conference talks and briefings.
  - **PDF Threat Report Parsing:** Automatic extraction of CVEs, Threat Actors, and network indicators directly from threat advisories.
- **RAG Analytics Engine:** (Retrieval-Augmented Generation) Hybrid vector & graph traversal querying utilizing local *Llama3* to interact with the ingested knowledge base, ensuring zero data leakage to public APIs.
- **Attack Path Emulation:** Native Neo4j shortest-path analytics to identify critical exploit chains in the environment.
- **2026-Grade 3D Visualization:** An interactive, hardware-accelerated force-directed graph (Three.js/D3) rendered globally across the platform. Featuring Volumetric Neon Bloom, node repulsion mechanics, and full semantic LLM-reasoning trace panes.

## 🚀 Getting Started

The system is fully containerized for straightforward deployment.

### Prerequisites

- Docker && Docker Compose
- Python 3.9+
- Ollama (installed locally)
- Llama3 Model (`ollama pull llama3`)

### Installation & Launch

You can boot the entire infrastructure, including the graphical environment and Neo4j database, with the included setup script:

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
3. Spin up the Neo4j Docker container in the background.
4. Launch the Streamlit application interface.

Access the platform organically at `http://localhost:8505` (or whichever port Streamlit binds to).

## 🛠 Architecture

CybersecLLM operates on a robust, entirely free tech stack:
- **Frontend / UI:** Streamlit (Python) acting as the connective tissue, rendering custom injected HTML/JS/CSS comprising `Three.js` and `3d-force-graph` for the visual engine.
- **Data Layer:** Neo4j Community Server handled via `neo4j` Python driver.
- **LLM Pipeline:** Langchain bindings wrapped around local `Ollama` sockets.

## 📄 Licensing

This project is licensed under the MIT License.

---
*Created and maintained by Prachyat Misra.*
