# Componente de Búsqueda Semántica - RRA

**Trabajo de Integración Curricular**
Escuela Politécnica Nacional (EPN)

Este repositorio contiene el código fuente de un componente de búsqueda semántica basado en la arquitectura de Generación Aumentada por Recuperación (RAG). El sistema está diseñado para la ingesta, procesamiento y consulta inteligente del Reglamento de Régimen Académico (RRA) de la institución.

##  Arquitectura de Directorios

El proyecto sigue un flujo de procesamiento de datos secuencial:

* **`data/`**: Contiene el corpus documental original (PDF) y los archivos resultantes de la limpieza y fragmentación estructurada (JSON).
* **`storage/`**: Directorio de persistencia local. Almacena los índices vectoriales serializados generados por LlamaIndex, minimizando la latencia de consulta.
* **`01_limpieza.py`**: *Script* de extracción y depuración inicial del texto normativo.
* **`02_jerarquia.py` / `02b_codificacion.py`**: Lógica de fragmentación estratégica (*chunking*) preservando metadatos, estructura legal y formato de codificación UTF-8.
* **`03_indexacion.py`**: Integración con el modelo `text-embedding-3-large` para la creación y guardado de los *embeddings* en la base de datos local.
* **`04_query.py`**: Interfaz de consola para la validación funcional del motor de inferencia generativo (`gpt-4o-mini`).
* **`05_app.py`**: Capa de presentación web desarrollada con Streamlit para la interacción y pruebas de retención de contexto transaccional.
* **`requirements.txt`**: Listado exacto de las dependencias y librerías necesarias para la ejecución.

##  Instrucciones de Ejecución

Para replicar el entorno de desarrollo y ejecutar el componente de forma local, siga estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/FaBrii-ID97/Componente-de-busqueda-semantica.git](https://github.com/FaBrii-ID97/Componente-de-busqueda-semantica.git)
   cd Componente-de-busqueda-semantica
2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt

3. **Cree un archivo llamado .env en la raíz del proyecto y añada su clave de acceso a la API:**
   ```bash
   OPENAI_API_KEY=clave_api_aqui

4. **Despliegue de capa de presentación**
   ```bash
   streamlit run 05_app.py
