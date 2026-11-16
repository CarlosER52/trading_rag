import sys
from src.rag_engine import build_rag_chain

def main():
    print("=" * 60)
    print(" 📈 QUANTTRADE RAG ENGINE - CONSOLE CLIENT ")
    print("=" * 60)
    print(" Inicializando motor (PostgreSQL + HuggingFace + Gemma 4)...")
    
    try:
        chain = build_rag_chain()
        print(" ¡Motor listo! Escribe tu consulta cuantitativa o 'salir' para terminar.\n")
    except Exception as e:
        print(f"❌ Error al inicializar el motor RAG: {e}")
        sys.exit(1)

    while True:
        try:
            pregunta = input("\n❓ Pregunta de Trading: ").strip()
            
            if not pregunta:
                continue
            
            if pregunta.lower() in ["salir", "exit", "quit"]:
                print("\n👋 ¡Hasta luego! Cerrando sesión de QuantTrade RAG.")
                break

            print("\n⏳ Analizando contexto y generando respuesta con Gemma 4...")
            respuesta = chain.invoke(pregunta)
            
            print("\n🤖 Respuesta:")
            print("-" * 50)
            print(respuesta)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\n👋 Sesión interrumpida. ¡Hasta pronto!")
            break
        except Exception as e:
            print(f"\n❌ Ocurrió un error procesando la consulta: {e}")

if __name__ == "__main__":
    main()