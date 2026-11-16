from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database import init_vector_store

DATA_DIR = Path("data")

def load_all_documents():
    """Escanea la carpeta data/ y carga automáticamente .md, .txt y .pdf de forma recursiva."""
    all_chunks = []
    
    # Mapeo de loaders según extensión
    loaders_map = {
        ".txt": lambda p: TextLoader(str(p), encoding="utf-8").load(),
        ".md": lambda p: TextLoader(str(p), encoding="utf-8").load(),
        ".pdf": lambda p: PyPDFLoader(str(p)).load(),
    }

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    # Buscar recursivamente en todas las subcarpetas de data/
    for file_path in DATA_DIR.glob("**/*"):
        if file_path.suffix.lower() in loaders_map:
            print(f"📄 Procesando archivo: {file_path}")
            try:
                loader_func = loaders_map[file_path.suffix.lower()]
                docs = loader_func(file_path)
                
                # Inyectar metadatos para la columna JSONB de PostgreSQL
                for doc in docs:
                    doc.metadata.update({
                        "source_file": file_path.name,
                        "file_type": file_path.suffix.lower(),
                        "category": file_path.parent.name
                    })
                
                chunks = text_splitter.split_documents(docs)
                print(f"   -> {len(chunks)} fragmentos generados de {file_path.name}")
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"❌ Error procesando {file_path.name}: {e}")

    print(f"✂️ Total general acumulado: {len(all_chunks)} fragmentos.")
    return all_chunks


def run_ingestion(clear_existing: bool = True) -> None:
    """Ejecuta el pipeline completo de ingesta multi-formato hacia PostgreSQL + pgvector."""
    print("--- Iniciando Pipeline de Ingesta Vectorial Multi-Formato ---")
    
    chunks = load_all_documents()
    
    if not chunks:
        print("⚠️ No se encontraron documentos para ingerir. Verifica la carpeta 'data/'.")
        return

    vectorstore = init_vector_store(collection_name="trading_knowledge_chunks")

    if clear_existing:
        print("🧹 Limpiando colección previa en PostgreSQL...")
        vectorstore.delete_collection()
        vectorstore = init_vector_store(collection_name="trading_knowledge_chunks")

    print("🚀 Vectorizando e insertando todos los fragmentos en PostgreSQL...")
    inserted_ids = vectorstore.add_documents(chunks)
    
    print(f"✅ Ingesta completada con éxito. Se almacenaron {len(inserted_ids)} vectores en total.")


if __name__ == "__main__":
    run_ingestion(clear_existing=True)