## Instrucciones de Ejecución

Para replicar el entorno de desarrollo y ejecutar el componente de forma local:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/FaBrii-ID97/Componente-de-busqueda-semantica
   cd Componente-de-busqueda-semantica

1) Crear y activar el entorno virtual:
```bash
   python -m venv venv
   .\venv\Scripts\activate
````

2) Instalar dependencias:
```bash
   pip install -r requirements.txt
```
4) Configurar las credenciales:crear un archivo llamado .env en la raíz del proyecto y colocar la clave de acceso a la API:
```bash
   OPENAI_API_KEY=clave_api_aqui
```
6) Desplegar capa presentacion:
```bash
   streamlit run 05_app.py
```
