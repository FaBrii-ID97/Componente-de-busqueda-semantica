import os
import sys
import logging
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# 1. CONFIGURACIÓN DE REGISTRO (LOGGING)
# Establece el nivel de registro en WARNING para minimizar la salida de consola
# durante la interacción del usuario y mantener limpia la interfaz del chat.
logging.basicConfig(
    level=logging.WARNING, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 2. CARGA DE CREDENCIALES DE ENTORNO
# Verifica la disponibilidad de la clave API antes de inicializar los modelos.
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: No se encontró la variable OPENAI_API_KEY en el entorno.")
    sys.exit(1)

# 3. CONFIGURACIÓN DEL MOTOR DE LENGUAJE (LLM) Y EMBEDDINGS
# Inicializa el modelo principal de generación. Se asigna un valor de temperatura de 0.1 
# para fomentar un comportamiento determinista, mitigando así el riesgo de alucinaciones.
Settings.llm = OpenAI(
    model="gpt-4o-mini", 
    temperature=0.1,
    system_prompt=(
        "Eres un asistente virtual académico experto en el Reglamento de Régimen Académico "
        "de la Escuela Politécnica Nacional (EPN) de Ecuador. Tu objetivo es responder dudas "
        "de los estudiantes de manera clara, directa y formal. "
        "REGLAS ESTRICTAS: "
        "1. Basa tus respuestas ÚNICAMENTE en la información proporcionada en el contexto. "
        "Puedes hacer inferencias lógicas si el usuario usa sinónimos o lenguaje coloquial "
        "(ej. 'perder una materia' = 'reprobar', 'no hacer trámites' = 'no matricularse' etc.), "
        "pero NUNCA inventes plazos, requisitos o reglas que no estén en el texto."
        "2. Si la respuesta no está en el contexto, responde: 'Lo siento, no encuentro esa información en el reglamento actual'. "
        "3. SIEMPRE debes citar explícitamente el Número de Artículo, Capítulo o Título en el que te basas."    )
)

# Configura el modelo de representación vectorial asegurando compatibilidad 
# con el modelo utilizado durante la fase de indexación.
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-large",
    dimensions=3072
)

from llama_index.core.memory import ChatMemoryBuffer # ¡Importante añadir este import arriba!

def cargar_asistente(storage_dir="storage"):
    """
    Rastrea el índice persistente y configura un Chat Engine 
    con memoria para mantener el historial de conversación.
    """
    print(f"Cargando base de conocimientos desde '{storage_dir}'...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        
        # --- CAMBIO AQUÍ: Reemplazamos query_engine por chat_engine ---
        # Definimos un buffer de memoria que guarda los últimos tokens
        memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
        
        # Creamos el Chat Engine
        chat_engine = index.as_chat_engine(
            chat_mode="condense_plus_context", # Condensa el historial para entender preguntas de seguimiento
            similarity_top_k=6,
            memory=memory,
            system_prompt=Settings.llm.system_prompt # Mantiene tu prompt estricto
        )
        return chat_engine # Ahora devuelve un chat_engine, no un query_engine
        
    except Exception as e:
        print(f"Error al cargar el índice: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Inicializa el motor de consultas cargando el índice en memoria.
    asistente = cargar_asistente()
    
    # Despliega la interfaz de la consola para la interacción del usuario.
    print("\n" + "="*60)
    print("🎓 ASISTENTE VIRTUAL EPN - REGLAMENTO ACADÉMICO 🎓")
    print("="*60)
    print("Escribe tu pregunta (o escribe 'salir' para terminar).\n")
    
    # Inicia el bucle principal de ejecución de consultas.
    while True:
        try:
            # Captura la entrada del usuario.
            pregunta = input("\n🧑‍🎓 Estudiante: ")
            
            # Condición de salida del bucle.
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego! Éxitos en tu semestre.")
                break
                
            # Omite entradas vacías.
            if not pregunta.strip():
                continue
                
            print("🤖 Consultando el reglamento...")
            
            # Ejecuta la búsqueda semántica y la generación de respuesta.
            respuesta = asistente.chat(pregunta)
            
            # Despliega el resultado de la inferencia.
            print(f"\n🏛️ Asistente EPN:\n{respuesta}\n")
            
        except KeyboardInterrupt:
            # Maneja la interrupción forzada desde el teclado (Ctrl+C).
            print("\n¡Hasta luego! Interrupción detectada.")
            break
        except Exception as e:
            # Captura y reporta errores imprevistos durante la generación.
            print(f"\n⚠️ Ocurrió un error general en la consulta: {e}")