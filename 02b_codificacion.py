import json

archivo_entrada = "data/conocimiento_epn.json"
archivo_salida = "data/conocimiento_epn_utf8.json"

try:
    # 1. Leer el archivo con la codificación original
    with open(archivo_entrada, 'r', encoding='windows-1252') as f:
        datos = json.load(f)
except UnicodeDecodeError:
    # 2. UTF-8 si falla la codificación anterior
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        datos = json.load(f)

# 3. Guardar el archivo con codificación UTF-8
with open(archivo_salida, 'w', encoding='utf-8') as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)

print(f"Archivo guardado correctamente como {archivo_salida}")