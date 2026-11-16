import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database import init_vector_store

# Ruta por defecto al archivo de conocimiento
DEFAULT_DATA_PATH = Path("data/trading_knowledge.txt")


def load_and_split_documents(file_path: Path = DEFAULT_DATA_PATH):
    """
    Carga el documento de texto y lo divide en fragmentos (chunks)
    preservando la coherencia semántica mediante splitting recursivo.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"❌ No se encontró el archivo de datos en: {file_path}")

    print(f"📄 Cargando documento desde: {file_path}")
    loader = TextLoader(str(file_path), encoding="utf-8")
    raw_documents = loader.load()

    # Inyectar metadatos adicionales para almacenamiento JSONB en PostgreSQL
    for doc in raw_documents:
        doc.metadata.update({
            "domain": "quantitative_trading",
            "category": "risk_management_and_metrics",
            "doc_version": "1.0"
        })

    # Estrategia de chunking recursivo
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = text_splitter.split_documents(raw_documents)
    print(f"✂️  Documento segmentado en {len(chunks)} fragmentos (chunks).")
    return chunks


def run_ingestion(clear_existing: bool = True) -> None:
    """
    Ejecuta el pipeline completo de ingesta hacia PostgreSQL + pgvector.
    """
    print("--- Iniciando Pipeline de Ingesta Vectorial ---")
    
    # 1. Cargar y segmentar
    chunks = load_and_split_documents()

    # 2. Inicializar vectorstore (HuggingFace Embeddings + PGVector)
    vectorstore = init_vector_store(collection_name="trading_knowledge_chunks")

    # 3. Limpiar colección previa si se solicita (garantiza idempotencia)
    if clear_existing:
        print("🧹 Limpiando vectores previos de la colección para evitar duplicados...")
        vectorstore.delete_collection()
        # Re-instanciar la colección limpia
        vectorstore = init_vector_store(collection_name="trading_knowledge_chunks")

    # 4. Generar embeddings e insertar en PostgreSQL
    print("🚀 Vectorizando e insertando fragmentos en PostgreSQL...")
    inserted_ids = vectorstore.add_documents(chunks)
    
    print(f"✅ Ingesta completada con éxito. Se almacenaron {len(inserted_ids)} vectores en 'trading_rag_db'.")


if __name__ == "__main__":
    run_ingestion(clear_existing=True)