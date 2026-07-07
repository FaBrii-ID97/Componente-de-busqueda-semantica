import json
import os
import sys
import logging
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURACIÓN DE REGISTRO (LOGGING)
# Establece el formato y el nivel de detalle para los mensajes de la consola.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 2. CARGA DE VARIABLES DE ENTORNO
# Obtiene las credenciales necesarias desde el archivo .env.
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("No se encontró la OPENAI_API_KEY en el entorno de ejecución.")
    sys.exit(1)

# 3. CONFIGURACIÓN GLOBAL DE LLAMAINDEX
# Define el modelo de embeddings predeterminado para las operaciones de vectorización.
# Se utiliza un modelo de alta dimensionalidad (3072 dimensiones) para capturar mayor precisión semántica.
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-large",
    dimensions=3072
)

class EPNIndexer:
    """
    Gestiona la transformación del texto estructurado en representaciones vectoriales.
    Se encarga de leer el archivo JSON, convertir los fragmentos en objetos 'Document' 
    y generar un índice vectorial persistente mediante LlamaIndex.
    """
    
    def __init__(self, json_path, storage_dir="storage"):
        # Inicializa las rutas del archivo de origen y el directorio de almacenamiento del índice.
        self.json_path = json_path
        self.storage_dir = storage_dir

    def load_documents(self):
        """
        Lee el archivo JSON de entrada, extrae el texto y los metadatos, y los 
        transforma en una lista de objetos 'Document' compatibles con LlamaIndex.
        """
        if not os.path.exists(self.json_path):
            logger.error(f"Archivo no encontrado: {self.json_path}")
            raise FileNotFoundError(self.json_path)

        try:
            # Lee el archivo asegurando la codificación UTF-8 para preservar caracteres en español.
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            documents = []
            for item in data:
                # Instancia un objeto Document asignando el contenido principal y sus metadatos asociados.
                doc = Document(
                    text=item.get("contenido", ""),
                    doc_id=item.get("id", ""),
                    metadata=item.get("metadata", {})
                )
                
                # Excluye el identificador del proceso de vectorización para evitar ruido semántico 
                # y enfocar el embedding exclusivamente en el contenido textual.
                doc.excluded_embed_metadata_keys = ["id"]
                documents.append(doc)
            
            logger.info(f"Carga exitosa: {len(documents)} documentos preparados para indexación.")
            return documents
            
        except Exception as e:
            logger.error(f"Error al procesar el archivo JSON: {e}")
            raise

    def create_index(self, documents):
        """
        Recibe la lista de documentos, genera sus vectores correspondientes mediante la API, 
        y almacena el índice resultante de forma local en el sistema de archivos.
        """
        try:
            logger.info("Iniciando fase de vectorización (esto puede tardar según el volumen de datos)...")
            
            # Construye el índice vectorial utilizando el almacén de datos nativo de LlamaIndex.
            index = VectorStoreIndex.from_documents(
                documents, 
                show_progress=True
            )
            
            # Verifica la existencia del directorio destino y lo crea en caso de ser necesario.
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
                
            # Persiste la estructura del índice vectorial en el disco local.
            index.storage_context.persist(persist_dir=self.storage_dir)
            logger.info(f"Índice guardado correctamente en el directorio: {self.storage_dir}")
            
        except Exception as e:
            logger.error(f"Fallo crítico durante la creación del índice: {e}")
            raise

if __name__ == "__main__":
    # Define las rutas de ejecución relativas al entorno.
    path_al_json = os.path.join("data", "conocimiento_epn_utf8.json")
    directorio_storage = "storage"
    
    try:
        # Instancia el indexador, carga los documentos y construye la base vectorial.
        indexer = EPNIndexer(path_al_json, directorio_storage)
        docs = indexer.load_documents()
        indexer.create_index(docs)
    except Exception as e:
        # Captura y registra cualquier error fatal no manejado internamente.
        logger.critical(f"El proceso de indexación finalizó con errores: {e}")
        sys.exit(1)