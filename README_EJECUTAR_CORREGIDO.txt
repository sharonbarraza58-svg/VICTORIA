VICTORIA - versión corregida

CAMBIOS PRINCIPALES
- Al abrir una Ficha, se abre directamente la pestaña Competencias.
- Competencias queda dentro de la Ficha; no se creó una segunda pantalla global de Competencias.
- La ficha conserva su título, programa, trimestre e instructor.
- La vista de Competencias muestra únicamente el trimestre real de esa ficha, evitando duplicar competencias o dejar columnas vacías de otros trimestres.
- Se conserva el acordeón de cada competencia y sus resultados de aprendizaje.
- Se conserva + Nuevo resultado.
- Se agregó un botón visible de Cerrar sesión en la barra superior.
- Se conservaron el logo VICTORIA, el estilo glass y las demás pantallas.
- Se agregaron al requirements.txt las dependencias que faltaban para el arranque: python-jose, email-validator, python-multipart y psycopg2-binary.

EJECUTAR EN WINDOWS / POWERSHELL

1. En VS Code abre esta carpeta (la carpeta donde está main.py).

2. Si todavía no existe el entorno virtual:
   python -m venv venv

3. Activar:
   .\venv\Scripts\Activate.ps1

4. Instalar dependencias:
   python -m pip install --upgrade pip
   pip install -r requirements.txt

5. Iniciar:
   uvicorn main:app --reload

6. Abrir en el navegador:
   http://127.0.0.1:8000

IMPORTANTE
- El archivo .env incluido apunta a PostgreSQL en 127.0.0.1:5432 con la base victoria.
- PostgreSQL debe estar encendido y la base de datos/configuración del .env debe existir.
- No ejecutes uvicorn desde Downloads si main.py está dentro de otra carpeta. Debes estar en la carpeta que contiene main.py.
