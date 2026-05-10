# ContextOS
Engineering Incident & Blocker Intelligence System

---

## Current Status — v0 Spike

The v0 spike proves the core data pipeline end-to-end:
- Parallel tool calls to Slack, GitHub, and Jira
- Context assembly with normalization, dedup, and sorting
- Cohere Command R+ generates a structured incident report
- Confidence degrades gracefully when sources are unavailable

No web server. No Slack bot. Just the engine.

---

## Project Structure

```
ContextOS/
├── src/
│   ├── mcp/
│   │   ├── slack_tool.py      # Fetch incident messages from Slack
│   │   ├── github_tool.py     # Fetch recent PRs + commits from GitHub
│   │   └── jira_tool.py       # Fetch incident tickets from Jira
│   ├── ai/
│   │   └── provider.py        # AIProvider Protocol + CohereProvider
│   └── core/
│       ├── schemas.py         # All Pydantic models
│       └── assembler.py       # Merge, dedup, sort, confidence score
├── spike.py                   # Entry point: runs the full v0 pipeline
├── .env.example
└── requirements.txt
```

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
```

Fill in your keys in `.env`:
- `COHERE_API_KEY` — Cohere API key
- `SLACK_BOT_TOKEN` — Slack bot token with `channels:history` scope
- `GITHUB_TOKEN` — GitHub personal access token
- `GITHUB_REPO` — target repo in `org/repo` format
- `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN` — Jira cloud credentials
- `SLACK_CHANNEL` — Slack channel ID to monitor (default: `incidents`)

**3. Run the spike**
```bash
python spike.py
```

Expected output: valid JSON with root cause, timeline, evidence, and postmortem draft.

---

## 🛠️ Tech stack

### Frontend
- Next.js  
- TypeScript  
- Tailwind CSS  
- shadcn/ui  

### Backend
- FastAPI (Python)  

### Database
- PostgreSQL  
- pgvector  

### AI
- Cohere Embed v3 (retrieval)  
- Cohere Rerank (ranking)  
- Cohere Command R+ (generation)  

### Integrations / Context Layer
- MCP (Model Context Protocol) for Slack, GitHub, Jira tool execution  

---

## ⚖️ Design constraints

- response latency: < 3 seconds (historical mode)  
- MCP live tool calls bounded by external API limits  
- max retrieved context: 10–15 chunks  
- incremental ingestion (no full re-sync)  
- caching for frequent queries and embeddings  
- graceful fallback from live MCP data → historical RAG when needed  

---

## 🧠 What ContextOS is

ContextOS is a **hybrid AI incident intelligence system**.

It combines:

- **RAG (Retrieval-Augmented Generation)** over historical engineering data  
- **MCP (Model Context Protocol)** for real-time tool execution  

Together, this allows the system to understand both:

- what has happened historically across engineering systems  
- what is happening right now in live Slack, GitHub, and Jira activity  

---

## 🔍 What problem it solves

Engineering work is fragmented across tools:

- Slack → discussions and incident signals  
- Jira → planning, blockers, and tickets  
- GitHub → code changes and implementation  

When something breaks, engineers currently must:

- manually search across multiple tools  
- reconstruct timelines from scattered signals  
- infer relationships between changes and incidents  
- rely on tribal knowledge  

This is slow, error-prone, and does not scale in modern engineering teams.

---

## 💡 Core idea

Instead of building a heavy graph system or AI “memory layer”, ContextOS focuses on a single goal:

> Reconstruct relevant engineering context across tools to explain incidents and blockers clearly, using both historical retrieval (RAG) and real-time tool execution (MCP).

---

## 🔄 How it works (high-level)

### 1. Data ingestion (historical layer)
ContextOS continuously pulls data from:
- Slack (channels, threads, incidents)
- GitHub (PRs, issues, commits)
- Jira (tickets, statuses, blockers)

Each item is normalized into an event document.

---

### 2. Indexing
Documents are embedded using Cohere Embed v3 and stored in pgvector.

Metadata includes:
- timestamp  
- source (Slack / GitHub / Jira)  
- related entities (PRs, tickets, services)  

---

### 3. Retrieval (RAG layer)
When a query is made:
- query is embedded  
- top-k similar documents are retrieved via vector search  
- metadata filters refine results  

---

### 4. Reranking
Cohere Rerank filters retrieved results to keep only the highest-signal evidence.

---

### 5. Context assembly
System:
- removes duplicates  
- filters low-signal noise  
- prioritizes recent + relevant events  
- groups cross-tool signals  

---

### 6. MCP live tool execution
If real-time context is needed, ContextOS uses MCP to:

- fetch live Slack messages  
- pull active GitHub PRs / deployments  
- retrieve Jira blockers in real time  

This enables answering:

- “What is causing the current outage?”
- “What just broke in production?”

---

### 7. Response generation
Cohere Command R+ generates:

- root cause explanation  
- step-by-step timeline  
- evidence with citations  
- fusion of live + historical context  
- confidence score  

---

## 🧩 Core use case

### Incident & blocker investigation

ContextOS is optimized for answering:

> “What is happening, why is it happening, and what is related to it?”

---

### Example 1: Deployment issue
“Why is the payments service deployment blocked?”

- Jira blocker ticket  
- Slack discussion thread  
- GitHub PR introducing breaking change  
- root cause explanation  

---

### Example 2: Outage investigation
“What caused the Redis latency spike?”

- incident timeline reconstruction  
- related PRs affecting caching layer  
- Slack incident response messages  
- infra ticket correlation  

---

### Example 3: Live incident
“What is causing the current outage?”

- live Slack incident messages (MCP)  
- active deployments (MCP)  
- open Jira blockers (MCP)  
- real-time root cause hypothesis  

---

## 🏗️ System architecture

Slack / GitHub / Jira  
↓  
MCP Tool Layer (live execution)  
↓  
Data Ingestion Layer  
↓  
Unified Document Store  
↓  
Cohere Embeddings  
↓  
Vector DB (pgvector)  
↓  
Hybrid Retrieval (vector + metadata)  
↓  
Cohere Rerank  
↓  
Context Assembly  
↓  
Command R+ Generation  
↓  
Structured Incident Response  

---

