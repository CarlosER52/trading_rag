import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.database import init_vector_store

load_dotenv()


def format_docs(docs) -> str:
    """Formatea los documentos recuperados de PostgreSQL en un bloque legible."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    """
    Construye el pipeline RAG completo utilizando LangChain Expression Language (LCEL),
    PostgreSQL (pgvector) como retriever y Google Gemma 4 vía OpenRouter.
    """
    # 1. Conectar al almacén vectorial existente en PostgreSQL
    vectorstore = init_vector_store(collection_name="trading_knowledge_chunks")
    
    # Configurar el retriever para extraer los 3 fragmentos más relevantes
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # 2. Configurar el LLM (Google Gemma 4 vía OpenRouter)
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    model_name = os.getenv("LLM_MODEL_NAME", "google/gemma-4-26b-a4b-it:free")

    if not api_key or api_key == "tu_openrouter_api_key_aqui":
        raise ValueError("❌ Falta configurar LLM_API_KEY válida en el archivo .env")

    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0.1,  # Baja temperatura para respuestas analíticas y deterministas
    )

    # 3. Plantilla de Prompt con control anti-alucinaciones
    system_template = """Eres un Analista Cuantitativo Senior especializado en gestión de riesgo algorítmico.
Responde a la consulta del usuario utilizando ÚNICAMENTE la información proporcionada en el siguiente contexto técnico.

Reglas estrictas:
1. Si la respuesta o fórmula exacta está en el contexto, preséntala de forma clara, directa y estructurada.
2. Si el contexto no contiene información suficiente para responder, indica explícitamente: "No dispongo de información sobre ese tema en la base de conocimiento actual." No inventes ni extrapoles reglas.

Contexto recuperado:
{context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "{question}")
    ])

    # 4. Ensamblaje del pipeline con LCEL
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


if __name__ == "__main__":
    # Prueba unitaria rápida del motor RAG
    print("⏳ Inicializando motor RAG (PGVector + Gemma 4)...")
    chain = build_rag_chain()
    
    pregunta_prueba = "¿Cuál es el límite de pérdida diaria y qué ocurre si se alcanza?"
    print(f"\n❓ Pregunta: {pregunta_prueba}\n")
    
    respuesta = chain.invoke(pregunta_prueba)
    print(f"🤖 Respuesta de Gemma 4:\n{respuesta}")