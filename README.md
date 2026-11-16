# 📈 QuantTrade RAG Engine

Motor de **Generación Aumentada por Recuperación (RAG)** modular diseñado para consultas técnicas sobre gestión de riesgo algorítmico, métricas cuantitativas, procedimientos operativos y whitepapers de arbitraje estadístico.

Construido con **LangChain Expression Language (LCEL)**, **PostgreSQL (`pgvector`)** para almacenamiento y búsqueda vectorial con metadatos JSONB, embeddings locales mediante **HuggingFace** y razonamiento generativo con **Google Gemma 4** vía OpenRouter.

---

## 🏗️ Arquitectura del Sistema Multi-Formato

```text
[data/] 
  ├── markdown/ (.md) ──► TextLoader     ──┐
  ├── pdfs/ (.pdf)     ──► PyPDFLoader   ──┼──► RecursiveChunking (500/80)
  └── txt/ (.txt)      ──► TextLoader     ──┘         │
                                                      ▼
[Embeddings Locales: all-MiniLM-L6-v2 (384 dims)]
                                                      │
                                                      ▼
[PostgreSQL 16 + pgvector (Metadatos JSONB)] ◄── Similitud Coseno (Top-K = 3)
                                                      │
                                                      ▼
[Pipeline LCEL + Grounding Anti-Alucinaciones]
                                                      │
                                                      ▼
[LLM: google/gemma-4-26b-a4b-it:free (OpenRouter)]
                                                      │
                                                      ▼
[CLI Interactivo (src/main.py)]