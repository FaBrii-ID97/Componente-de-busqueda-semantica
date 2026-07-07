import streamlit as st
import os
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# 1. CONFIGURACIÓN DE LA PÁGINA
# Establece los parámetros visuales iniciales de la interfaz web, 
# definiendo el título de la pestaña, el ícono y la alineación del contenido.
st.set_page_config(page_title="Asistente EPN", page_icon="🎓", layout="centered")

# 2. CARGA DE CREDENCIALES
# Verifica la existencia de las variables de entorno necesarias. 
# Si la clave de la API no está presente, detiene la ejecución de la aplicación web.
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("No se encontró la OPENAI_API_KEY. Revisa archivo .env")
    st.stop()

# 4. CONFIGURACIÓN DEL MOTOR Y CACHÉ
# El decorador @st.cache_resource asegura que la inicialización de los modelos 
# y la carga del índice se realicen una sola vez, optimizando el rendimiento 
# y evitando recargas innecesarias cada vez que el usuario interactúa con la interfaz.
@st.cache_resource
def obtener_indice():
    """
    Configura los parámetros globales de LlamaIndex (LLM y Embeddings) y 
    restaura el índice vectorial desde el almacenamiento local.
    """
    Settings.llm = OpenAI(
        model="gpt-4o-mini", 
        temperature=0.1,
        system_prompt=(
            "Eres un asistente virtual académico experto en el Reglamento de Régimen Académico de la EPN. "
            "Responde de manera clara, directa y formal basándote estrictamente en el contexto. "
            "Si la información no está, indica que no se encuentra en el reglamento actual. "
            "Cita siempre el Artículo correspondiente. "
            "Si el usuario saluda o agradece, responde cortésmente sin citar leyes."
            "Posees la capacidad de interpretar el lenguaje coloquial y la jerga universitaria común en el contexto ecuatoriano y de la EPN. "
            "Cuando el usuario utilice términos informales, debes relacionarlos con los conceptos oficiales del reglamento. "
        )
    )
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", dimensions=3072)
    
    # Restaura la base de conocimientos desde el directorio local "storage".
    storage_context = StorageContext.from_defaults(persist_dir="storage")
    return load_index_from_storage(storage_context)

# 5. INICIALIZACIÓN DE LA SESIÓN Y MEMORIA
# Instancia el índice utilizando la función almacenada en caché.
indice = obtener_indice()

# Configura el motor de chat persistente en el estado de la sesión (session_state).
# Esto previene que el historial de la conversación se borre al refrescar la página.
if "chat_engine" not in st.session_state:
    # Se habilita el modo "condense_plus_context" para reformular preguntas ambiguas 
    # y se integra el ChatMemoryBuffer para retener el contexto de turnos previos.
    st.session_state.chat_engine = indice.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=3000),
        similarity_top_k=6
    )

# Inicializa el contenedor visual del historial de mensajes si es la primera interacción.
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de la EPN. ¿Qué duda reglamentaria tienes hoy?"}
    ]

# 6. DISEÑO DE LA INTERFAZ
# Renderiza los elementos estáticos del encabezado de la aplicación web.
st.title("🎓 Asistente Virtual EPN")
st.caption("Responderé tus preguntas relacionadas con el Reglamento de Régimen Académico de la Escuela Politécnica Nacional. ¡Pregunta lo que necesites saber!")
st.divider()

# Itera sobre la lista de mensajes almacenada en la sesión y los renderiza en la pantalla
# para mantener el historial visual de la conversación.
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. PROCESAMIENTO DE CONSULTA
# Despliega el campo de entrada de texto y captura la petición del usuario.
if prompt_usuario := st.chat_input("Escribe tu duda aquí..."):
    # Registra y muestra inmediatamente el mensaje del usuario en la interfaz.
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)
        
    # Inicializa el bloque de respuesta del asistente informático.
    with st.chat_message("assistant"):
        # Muestra un indicador visual de carga (spinner) mientras el modelo procesa la respuesta.
        with st.spinner("Analizando reglamento..."):
            try:                
                # Ejecuta la consulta a través del motor orquestador con memoria.
                response = st.session_state.chat_engine.chat(prompt_usuario)
                respuesta_texto = response.response
                
                # Despliega la respuesta generada y la guarda en el historial de la sesión.
                st.markdown(respuesta_texto)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_texto})
            except Exception as e:
                # Captura excepciones en tiempo de ejecución y muestra un bloque de error en la UI.
                st.error(f"Error técnico: {str(e)}")