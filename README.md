# ContextOS

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
- MCP (Model Context Protocol) for Slack, GitHub, Jira connectors  

---

## ⚖️ Design constraints

- response latency: < 3 seconds  
- max retrieved context: 10–15 chunks  
- incremental ingestion (no full re-sync)  
- API rate limit handling (Slack/GitHub/Jira via MCP tools)  
- caching for frequent queries and embeddings  

---

## 🧠 What ContextOS is

ContextOS is a **focused incident intelligence system**.

It connects engineering tools through MCP-powered integrations and builds a unified retrieval layer that reconstructs what happened across Slack, GitHub, and Jira when incidents or blockers occur.
