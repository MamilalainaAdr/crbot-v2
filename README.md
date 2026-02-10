# crbot
Local RAG-powered code review tool using Llama 3.2 + ChromaDB for quality/security analysis.

### Overview
- `llm_client.py` – HTTP client for Ollama  
- `code_scanner.py` – Detects code files to be analyzed  
- `collect_texts.py` – Extracts documentation from `data_repos/` into `dataset/`  
- `build_index.py` – Builds a Chroma index (RAG of best‑practice docs)  
- `search_index.py` – Tests searching within the index  
- `build_project_overview.py` – Generates a global overview of the codebase (summary per file)  
- `review_file.py` – Advanced review of a single file (RAG + global view + neighboring files)  
- `review_project.py` – Aggregates reviews of all files in the project  
- `cli.py` – Command‑line interface for **crbot** (commands: `index`, `overview`, `review`)

