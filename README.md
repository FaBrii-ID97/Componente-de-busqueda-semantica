# Asistente Virtual Inteligente para Consulta de Reglamentación de la EPN
# Componente de Búsqueda Semántica
> Motor de recuperación de información basado en arquitectura RAG para el procesamiento y consulta inteligente del Reglamento de Régimen Académico.
 
---
 
## Información General
 
| Campo | Información |
|--------|-------------|
| Institución | Escuela Politécnica Nacional |
| Facultad | Facultad de Ingeniería Eléctrica y Electrónica |
| Carrera | Tecnologías de la Información |
| Asignatura | Trabajo de Integración Curricular |
| Autor | Fabricio Alexander Tixe Chicaiza |
| Director | Raúl David Mejía Navarrete |
| Año | 2026 |
| Versión | 1.0 |
 
---
 
# Tabla de Contenidos
 
- [Descripción del Proyecto](#descripción-del-proyecto)
- [Objetivos](#objetivos)
- [Alcance](#alcance)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura](#arquitectura)
- [Licencia](#licencia)
 
---
 
# Descripción del Proyecto
 
El componente de búsqueda semántica es el núcleo de un sistema de recuperación semántica sobre normativa institucional. El componente se desarrolló usando el lenguaje de programación Python, implementando un flujo de datos bajo una arquitectura RAG (Generación Aumentada por Recuperación) que usa como orquestador el *framework* LlamaIndex. El trabajo realizado se divide en las siguientes fases secuenciales: 
 
* **Procesamiento y estructuración de datos:** El flujo comienza con la adecuación del documento normativo, en este caso el Reglamento de Régimen Académico (RRA) de la Escuela Politécnica Nacional. A través de *scripts* de Python, el texto original fue depurado de información innecesaria como pies de página y encabezados. Luego, se implementó una segmentación jerárquica para separar títulos, capítulos y artículos, generando un archivo JSON estructurado a partir del texto plano procesado. Esta fase es indispensable para asegurar que el texto conserve sus metadatos y contexto completo previo a su interacción con los modelos de inteligencia artificial. 
* **Indexación vectorial y persistencia:** LlamaIndex dispone de clases que ingieren el archivo JSON; en esta fase el sistema se enlaza con la API de OpenAI con el fin de transformar cada artículo del corpus normativo en vectores, a través del modelo `text-embedding-3-large`. Para reducir el consumo continuo de la API externa, se implementó un índice vectorial dentro del almacenamiento local del servidor en el directorio `/storage`, para obtener una base de consultas rápida. 
* **Recuperación semántica y generación de respuestas:** Se diseñó el motor en tiempo de ejecución, el cual, al recibir una pregunta del usuario, transforma en vector esa consulta y ejecuta una búsqueda de similitud matemática sobre la base de índice vectorial local para obtener solamente los artículos relacionados a la duda del usuario. Esta información se administra como contexto al modelo de lenguaje `gpt-4o-mini`. Adicionalmente, mediante instrucciones del sistema, se restringió al modelo para que provea una respuesta sujetándose estrictamente a la información que se encuentra en el RRA y obligando a citar el artículo relacionado a la consulta, con el fin de reducir posibles respuestas erradas. 
 
---
 
# Objetivos
 
## Objetivo General
 
* Desarrollar un componente de búsqueda semántica que procese el corpus normativo de la EPN mediante técnicas de vectorización y *embeddings*, integradas con un modelo de lenguaje de gran escala, para generar respuestas precisas basadas en la reglamentación institucional.
 
## Objetivos Específicos
 
* Diseñar la estrategia de segmentación jerárquica y generación de *embeddings* del corpus normativo de la EPN, definiendo el modelo de representación vectorial de alta dimensionalidad y los parámetros de persistencia para su almacenamiento local. 
* Implementar el sistema de recuperación semántica utilizando el *framework* LlamaIndex para indexar los *embeddings* y permitir la búsqueda eficiente de fragmentos normativos relevantes mediante una arquitectura de almacenamiento persistente. 
* Evaluar el funcionamiento del componente mediante la integración con un modelo de lenguaje de gran escala (`gpt-4o-mini`) y la ejecución de casos de prueba que validen la precisión, la coherencia y la correcta citación de fuentes en las respuestas generadas. 
 
---
 
# Alcance
 
El desarrollo de este componente se centra en la implementación de la lógica de búsqueda y recuperación semántica de un motor RAG, incluyendo el despliegue de una capa de presentación para su adecuada validación funcional. El proyecto se gestionará bajo la metodología ágil SCRUM. Para la planificación de las iteraciones, el alcance técnico se ha estructurado en las siguientes fases de desarrollo: 
 
**1. Fase de acondicionamiento del corpus documental**
* El alcance de los datos se delimita exclusivamente al Reglamento de Régimen Académico de la institución. 
* En esta etapa se ejecuta la extracción del texto original, seguida de su depuración y división estratégica (*chunking*). La información se organiza bajo una estructura JSON, asegurando que cada bloque normativo mantenga su integridad jurídica y su nivel jerárquico dentro del documento. 
 
**2. Fase de modelado y vectorización semántica**
* Para la traducción de los textos a representaciones matemáticas, se implementa el modelo `text-embedding-3-large` de OpenAI.
* Mediante *scripts* desarrollados en Python, los fragmentos normativos previamente estructurados se procesan y convierten en vectores densos compuestos por 3.072 dimensiones. 
 
**3. Fase de despliegue de la arquitectura RAG (LlamaIndex)**
* Se establece LlamaIndex como el *framework* principal del flujo de datos. Integra el módulo `ChatMemoryBuffer` para conservar el estado de las variables y mantener la persistencia lógica en interacciones continuas. 
* Los vectores generados se resguardan en un índice persistente dentro de un directorio local.
* Se vectoriza la consulta de entrada para extraer los fragmentos institucionales más coincidentes. Estos datos alimentan al LLM `gpt-4o-mini` a través de plantillas de *prompts* optimizadas.
 
**4. Fase de validación de la capa de presentación**
* Se desarrolla una interfaz de validación en un entorno web local utilizando el *framework* Streamlit. 
* El alcance se restringe exclusivamente al despliegue de una capa de presentación que permite la interacción y el envío de peticiones HTTP al motor de inferencia. El diseño de arquitecturas de experiencia de usuario, la autenticación de credenciales institucionales o la gestión de perfiles estudiantiles quedan fuera de los límites de esta investigación. 
 
**5. Fase de Evaluación y Sintonización**
* El componente se somete a casos de prueba diseñados para certificar el asertividad de las búsquedas semánticas y corroborar el correcto tratamiento de caracteres especiales en español (codificación UTF-8). 
* Se calibran los hiperparámetros del componente, incluyendo la fijación de la temperatura del modelo generativo y el refinamiento de las instrucciones maestras para blindar las respuestas contra alucinaciones.
 
---
 
# Tecnologías Utilizadas
 
| Tecnología | Versión |
|------------|---------|
| Python | 3.10+ |
| LlamaIndex | (Última estable) |
| Streamlit | (Última estable) |
| OpenAI API (`gpt-4o-mini`, `text-embedding-3-large`) | (Última estable) |
 
---
 
# Arquitectura
 
El sistema sigue un flujo de procesamiento secuencial estructurado en cinco fases: limpieza del texto original, segmentación jerárquica preservando metadatos, indexación vectorial en almacenamiento local persistente, recuperación semántica por similitud de cosenos y, finalmente, generación de respuestas a través del modelo de inferencia. La interacción del usuario se gestiona mediante una interfaz web transaccional.
 
*(La arquitectura más detallada se encuentra en el documento del Trabajo de Integración Curricular).*
 
---
 
# Licencia
 
Este proyecto fue desarrollado con fines académicos como parte del Trabajo de Integración Curricular de la carrera de Tecnologías de la Información.
 
Su distribución y uso quedan sujetos a la normativa institucional correspondiente.
