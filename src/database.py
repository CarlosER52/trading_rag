import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

load_dotenv()


def get_database_connection() -> str:
    """Obtiene la URL de conexión a PostgreSQL desde las variables de entorno."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/trading_rag_db"
    )


def check_postgres_health() -> bool:
    """Verifica conexión física con PostgreSQL y que la extensión pgvector exista."""
    conn_str = get_database_connection()
    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa al motor PostgreSQL.")

            result = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
            ).fetchone()

            if result:
                print("✅ Extensión 'pgvector' detectada y operativa.")
            else:
                print("⚠️ Conectado a PostgreSQL, pero falta ejecutar: CREATE EXTENSION vector;")
                return False
        return True
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False


def init_vector_store(collection_name: str = "trading_knowledge_chunks") -> PGVector:
    """
    Inicializa el modelo de embeddings local (HuggingFace)
    y la conexión al almacén vectorial en PostgreSQL (pgvector).
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    connection_string = get_database_connection()

    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string,
        use_jsonb=True,
    )
    return vectorstore


if __name__ == "__main__":
    print("--- Iniciando diagnóstico de infraestructura ---")
    if check_postgres_health():
        print("⏳ Cargando modelo de embeddings local (all-MiniLM-L6-v2)...")
        vs = init_vector_store()
        test_vector = vs.embeddings.embed_query("prueba de conexión cuantitativa")
        print(f"✅ Embeddings operativos (Dimensión del vector: {len(test_vector)}).")
        print("✅ PGVector inicializado correctamente.")
        print("\n🚀 ¡Todo listo! La base de datos y los embeddings funcionan correctamente.")