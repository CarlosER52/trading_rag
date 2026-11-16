# 📈 QuantTrade RAG Engine

Motor de **Generación Aumentada por Recuperación (RAG)** modular diseñado para consultas técnicas sobre gestión de riesgo algorítmico, métricas cuantitativas y protocolos de ejecución en trading.

Construido con **LangChain Expression Language (LCEL)**, **PostgreSQL (`pgvector`)** para almacenamiento y búsqueda vectorial, embeddings locales mediante **HuggingFace** y razonamiento generativo con **Google Gemma 4** vía OpenRouter.

---

## 🏗️ Arquitectura del Sistema

```text
[data/trading_knowledge.txt]
          │
          ▼  (TextLoader + RecursiveCharacterTextSplitter: 500/80)
[Embeddings Locales: all-MiniLM-L6-v2 (384 dims)]
          │
          ▼  (Inserción Vectorial + Metadatos JSONB)
[PostgreSQL 16 + pgvector] ◄─── Similitud Coseno (Top-K = 3)
          │
          ▼  (Pipeline LCEL + Grounding Anti-Alucinaciones)
[LLM: google/gemma-4-26b-a4b-it:free (OpenRouter)]
          │
          ▼
[CLI Interactivo (src/main.py)]