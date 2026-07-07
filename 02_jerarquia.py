import json
import re
import os
import logging

# Establece la configuración básica para el registro de eventos en la consola.
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class EPNKnowledgeBuilder:
    """
    Gestiona la construcción de la jerarquía de conocimientos a partir 
    del Reglamento de Régimen Académico de la EPN. 
    Segmenta el texto en Títulos, Capítulos, Artículos y Disposiciones.
    """
    
    def __init__(self, input_path: str, output_path: str):
        # Inicializa las rutas de los archivos de entrada y salida.
        self.input_path = input_path
        self.output_path = output_path
        
        # Define las expresiones regulares para identificar la estructura general del documento.
        self.regex_titulo = re.compile(r"(T[ÍI]TULO\s+[IVXLCDM]+(?:\.-)?.*?)(?=Cap[íi]tulo|Art|Parte|$)", re.IGNORECASE)
        self.regex_capitulo = re.compile(r"(CAP[ÍI]TULO\s+[IVXLCDM]+(?:\.-)?.*?)(?=Art|Parte|$)", re.IGNORECASE)
        
        # Define las expresiones regulares para realizar los cortes principales del texto.
        self.regex_articulo_split = re.compile(r"(Art[íi]culo\s+\d+\.-)", re.IGNORECASE)
        self.regex_disposicion_split = re.compile(r"(DISPOSICI[ÓO]N\s+(?:GENERAL|DEROGATORIA|TRANSITORIA|FINAL)\s+[A-ZÚ]+(?:\.-)?)", re.IGNORECASE)

    def build_hierarchy(self) -> None:
        """
        Procesa el archivo de entrada JSON, extrae la jerarquía de los artículos 
        y disposiciones, y exporta el resultado estructurado en un nuevo archivo JSON.
        """
        # Verifica la existencia del archivo de entrada; si no existe, registra un error y detiene la ejecución.
        if not os.path.exists(self.input_path):
            logging.error(f"El archivo de entrada no existe: {self.input_path}")
            return

        # Registra el inicio del proceso en la consola.
        logging.info("Iniciando la generación de la jerarquía (Artículos y Disposiciones)...")
        
        # Abre y lee el contenido del archivo de entrada.
        with open(self.input_path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        # 1. Unifica el texto completo.
        # Extrae el contenido de cada bloque utilizando el método .get() para prevenir errores por claves inexistentes.
        full_text = " ".join([chunk.get("contenido", "") for chunk in raw_data])
        
        # 2. Divide el texto completo utilizando la palabra "Artículo" como separador.
        parts = self.regex_articulo_split.split(full_text)
        structured_knowledge = []
        
        # Almacena el contexto o los considerandos iniciales (el texto ubicado antes del primer artículo).
        initial_context = parts[0].strip()
        if initial_context:
            structured_knowledge.append({
                "id": "CONTEXTO-INICIAL",
                "metadata": {"tipo": "Considerandos"},
                "contenido": initial_context
            })

        # Establece los valores por defecto para el seguimiento de la jerarquía.
        current_title = "I"
        current_cap = "0"
        last_body = ""

        # 3. Procesa de manera iterativa los fragmentos resultantes.
        for i in range(1, len(parts), 2):
            header = parts[i]
            body = parts[i+1]
            
            # Extrae el número del artículo actual o le asigna "S/N" si carece de numeración.
            art_num_match = re.search(r"(\d+)", header)
            art_num = art_num_match.group(1) if art_num_match else "S/N"

            # Detecta y actualiza los cambios de Título que se encuentren dentro del texto.
            tit_match = self.regex_titulo.search(body)
            if tit_match:
                next_title_text = tit_match.group(1)
                body = body.replace(next_title_text, "").strip()
                romano = re.search(r"([IVXLCDM]+)", next_title_text)
                if romano: 
                    current_title = romano.group(1)

            # Detecta y actualiza los cambios de Capítulo que se encuentren dentro del texto.
            cap_match = self.regex_capitulo.search(body)
            if cap_match:
                next_cap_text = cap_match.group(1)
                body = body.replace(next_cap_text, "").strip()
                romano_cap = re.search(r"([IVXLCDM]+)", next_cap_text)
                if romano_cap: 
                    current_cap = romano_cap.group(1)

            # Aplica un tratamiento especial al último artículo para separar las disposiciones finales del cuerpo del texto.
            if i + 2 >= len(parts):
                last_body = body
                clean_body = self.regex_disposicion_split.split(body)[0]
                body = clean_body

            # Agrega el artículo procesado a la lista estructurada con sus respectivos metadatos.
            structured_knowledge.append({
                "id": f"T{current_title}-C{current_cap}-A{art_num}",
                "metadata": {
                    "tipo": "Articulo",
                    "titulo": current_title,
                    "capitulo": current_cap,
                    "articulo": art_num
                },
                "contenido": f"{header} {body.strip()}"
            })

        # 4. Procesa las disposiciones finales si se encontraron en el último bloque.
        if last_body:
            disp_parts = self.regex_disposicion_split.split(last_body)
            # Omite el primer índice ya que corresponde al texto del último artículo, y procesa el resto.
            for j in range(1, len(disp_parts), 2):
                d_header = disp_parts[j]
                d_body = disp_parts[j+1]
                structured_knowledge.append({
                    "id": f"DISPOSICION-{j//2 + 1}",
                    "metadata": {"tipo": "Disposicion"},
                    "contenido": f"{d_header} {d_body.strip()}"
                })

        # 5. Exporta los datos estructurados al archivo de destino.
        # Asegura la correcta escritura de caracteres especiales en español mediante ensure_ascii=False.
        with open(self.output_path, "w", encoding="utf-8") as file:
            json.dump(structured_knowledge, file, ensure_ascii=False, indent=4)
        
        # Registra la finalización exitosa del proceso y detalla la cantidad de nodos construidos.
        logging.info(f"Proceso finalizado. Se generaron {len(structured_knowledge)} nodos en {self.output_path}.")


if __name__ == "__main__":
    # Define las rutas relativas de los archivos y ejecuta el constructor de la clase principal.
    ruta_entrada = os.path.join("data", "reglamentoLimpio.json")
    ruta_salida = os.path.join("data", "conocimiento_epn.json")
    
    builder = EPNKnowledgeBuilder(ruta_entrada, ruta_salida)
    builder.build_hierarchy()