# ORIN AI Engine

Python intelligence layer for ORIN adaptive academic learning.

This repo is intentionally separate from the mobile app and Node backend. It keeps heavy Python AI/ML dependencies, generated vector indexes, OCR/RAG tooling, and future adaptive-learning models out of the production app/backend deploy path until integration is ready.

It builds reusable academic intelligence assets:

- semantic textbook chunks
- concept-level embeddings
- ChromaDB vector index
- optional FAISS index
- topic dependency graph
- retrieval with syllabus metadata filters
- question/context analysis scaffolding

## Repo Safety

Commit source and docs only:

- `orin_ai_engine/`
- `README.md`
- `PHASE2_REPORT.md`
- `requirements.txt`
- `requirements-torch.txt`
- `.gitignore`

Do not commit generated/runtime assets:

- `.venv/`
- `storage/`
- ChromaDB/FAISS indexes
- graph output files
- caches
- secrets
- raw PDFs

## Setup

```powershell
cd orin-ai-engine
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m spacy download en_core_web_sm
```

PyTorch can be installed later when deeper ML training is needed:

```powershell
.\.venv\Scripts\pip install -r requirements-torch.txt
```

## Build SSC Indexes

```powershell
.\.venv\Scripts\python -m orin_ai_engine.index_builder --board SSC --class 10
```

Build SSC Classes 6-10:

```powershell
.\.venv\Scripts\python -m orin_ai_engine.index_builder --board SSC --classes 6,7,8,9,10
```

Generated output is written under `storage/` and can be rebuilt any time from backend academic data.

## Retrieval Smoke Tests

```powershell
.\.venv\Scripts\python -m orin_ai_engine.retrieval --board SSC --class 10 --subject Mathematics --chapter "Real Numbers" --query "why use Euclid division lemma for HCF"
.\.venv\Scripts\python -m orin_ai_engine.retrieval --board SSC --class 8 --subject Physics --query "mirror reflection ray diagram"
.\.venv\Scripts\python -m orin_ai_engine.retrieval --board SSC --class 6 --subject Science --query "food components and nutrition"
```

The engine reads academic data from:

- `orin-backend/data/academics/final_dataset`
- `orin-backend/data/academics/orin_academic_dataset.json`

Output indexes are written under:

- `orin-ai-engine/storage/chroma`
- `orin-ai-engine/storage/faiss`
- `orin-ai-engine/storage/graphs`

## Phase 2 Metadata

Each semantic chunk now carries:

- board/class/subject/chapter/topic
- syllabus path
- chunk type
- extracted concepts
- prerequisite hints when present
- question category when the chunk is a textbook question
- difficulty and page metadata where available

Retrieval uses hybrid scoring:

- embedding similarity
- subject/chapter filter bonus
- concept overlap bonus
- topic/definition/question evidence bonus

## Phase 3 Direction

The next integration step should expose this engine as a small read-only service for the Node backend:

- retrieval context
- question analysis
- student mastery scoring
- adaptive roadmap context

The backend should call this service through an API boundary. It should not import Python modules directly, and it should not mutate student learning records through the AI engine until the read-only integration is stable.
