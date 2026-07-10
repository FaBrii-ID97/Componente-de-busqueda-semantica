Crear y activar entorno virtual
2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
# Windows:
.\venv\Scripts\activate
   .\venv\Scripts\activate

Instalar las dependencias:
pip install -r requirements.txt
3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt

Cree un archivo llamado .env en la raíz del proyecto y añada su clave de acceso a la API:
OPENAI_API_KEY=clave_api_aqui
3. **Cree un archivo llamado .env en la raíz del proyecto y añada su clave de acceso a la API:**
   ```bash
   OPENAI_API_KEY=clave_api_aqui

Despliegue de capa de presentación
streamlit run 05_app.py
4. **Despliegue de capa de presentación**
   ```bash
   streamlit run 05_app.py
