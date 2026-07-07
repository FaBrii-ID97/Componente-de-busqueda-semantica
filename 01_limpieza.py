import pdfplumber
import re
import os
import json

class ReglamentoCleaner:
    """
    Clase responsable de la extracción y depuración del contenido del documento PDF.
    Se encarga de leer el archivo, remover encabezados y pies de página institucionales,
    e identificar tanto texto plano como tablas para estructurarlos en un formato intermedio.
    """
    
    def __init__(self, input_path, output_path):
        # Inicializa las rutas del archivo PDF de entrada y el archivo JSON de salida.
        self.input_path = input_path
        self.output_path = output_path
        
        # Define una lista de expresiones regulares que representan el texto "basura"
        # u ofimático que se repite en el documento y que no aporta valor semántico.
        self.patterns = [
            r"ESCUELA POLITÉCNICA NACIONAL",
            r"CONSEJO POLITÉCNICO",
            r"Campus Politécnico.*",
            r"Ladrón de Guevara.*Quito – Ecuador",
            r"Página \d+ de \d+",
            r"Teléfonos:.*",
            r"Fax:.*",
            r"Apartados:.*"
        ]

    def clean_text(self, text):
        """
        Aplica las expresiones regulares para eliminar el texto institucional irrelevante
        y normaliza los espacios en blanco del texto extraído.
        """
        # Verifica que exista texto para limpiar; de lo contrario, retorna una cadena vacía.
        if not text:
            return ""
            
        # Itera sobre la lista de patrones y los reemplaza por cadenas vacías.
        for pattern in self.patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
        # Reemplaza múltiples saltos de línea o espacios consecutivos por un único espacio.
        text = re.sub(r'\s+', ' ', text)
        
        # Retorna el texto limpio sin espacios al inicio o al final.
        return text.strip()

    def process_document(self):
        """
        Abre el documento PDF, extrae secuencialmente las tablas y el texto página por página,
        aplica la limpieza correspondiente y guarda la información en una lista estructurada.
        """
        # Verifica la existencia del archivo PDF antes de iniciar el proceso.
        if not os.path.exists(self.input_path):
            print(f"Error: No se encuentra el archivo {self.input_path}")
            return

        print("Iniciando extracción técnica...")
        raw_chunks = []

        # Abre el archivo PDF utilizando la librería pdfplumber.
        with pdfplumber.open(self.input_path) as pdf:
            for i, page in enumerate(pdf.pages):
                
                # 1. Extracción de tablas de la página actual.
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Limpia los saltos de línea dentro de las celdas y descarta celdas vacías.
                        clean_row = [str(cell).replace('\n', ' ').strip() for cell in row if cell]
                        if clean_row:
                            # Agrega la fila de la tabla a la lista, separando sus columnas con el carácter '|'.
                            raw_chunks.append({
                                "tipo": "tabla",
                                "contenido": f"DATOS_TABLA: {' | '.join(clean_row)}",
                                "pagina_original": i + 1
                            })

                # 2. Extracción y limpieza del texto base de la página actual.
                text = self.clean_text(page.extract_text())
                if text:
                    # Agrega el bloque de texto limpio a la lista.
                    raw_chunks.append({
                        "tipo": "texto",
                        "contenido": text,
                        "pagina_original": i + 1
                    })

        # Exporta la lista de fragmentos crudos a un archivo JSON.
        # El parámetro ensure_ascii=False asegura que las tildes y eñes se guarden correctamente.
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(raw_chunks, f, ensure_ascii=False, indent=4)
        
        print(f"Proceso finalizado. JSON intermedio generado: {self.output_path}")

if __name__ == "__main__":
    # Define las rutas relativas para el documento de entrada y el archivo de salida.
    INPUT_PDF = "data/reglamento.pdf"
    OUTPUT_JSON = "data/reglamentoLimpio.json"
    
    # Instancia la clase limpiadora y ejecuta el flujo de procesamiento.
    cleaner = ReglamentoCleaner(INPUT_PDF, OUTPUT_JSON)
    cleaner.process_document()