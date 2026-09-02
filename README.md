//////////////////////////////////
NOTA DE LA CORRECCION (leer antes de correr el proyecto)
//////////////////////////////////

Este proyecto fue auditado y corregido. Pasos para dejarlo funcionando:

1. Crea tu entorno virtual y activalo (paso 1 y 2 de abajo, sin cambios).
2. Instala TODAS las dependencias de una sola vez con:
     pip install -r requirements.txt
   (requirements.txt ya viene limpio: se quito "dotenv" -que chocaba con
   "python-dotenv"- y "PyMySQL" -que no se usa, la base es PostgreSQL-, y
   se agregaron "python-jose" y "python-multipart", que el proyecto
   necesita para JWT y para el formulario de login pero nunca habian
   quedado registrados en el archivo.)
3. Revisa tu archivo .env: ahora, ademas de DATABASE_URL, DEBE tener
   SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES y ALLOWED_ORIGINS.
   Sin estas variables el servidor ya NO arranca (a proposito: es una
   falla segura para que nunca corra con configuracion insegura).
4. Corre las migraciones de Alembic (pasos 8-9 de abajo). El archivo
   alembic/env.py tenia un import roto que impedia ejecutar CUALQUIER
   comando de alembic; ya esta corregido.
5. uvicorn main:app --reload

//////////////////////////////////
SENTENCIAS
/////////////////////////////////


1 . python -m venv venv                                                                                                    
2 . .\venv\Scripts\activate                                                                                                
4 . pip install fastapi uvicorn                                                                                         .
5 . pip install sqlalchemy pymysql dotenv  * // si hay un error con la terminal o apesar de que las bibliotecas estan instaldas entonces contr shitf p  Python: Select Interpreter
6 . pip install pydantic-settings
7 . pip freeze > requirements.txt                 
8 . pip install psycopg2-binary
10 . pip install python-multipart
python -c "import secrets; print(secrets.token_hex(32))"
env\Scripts\python -m pip install "python-jose[cryptography]" python-multipart python-dotenv  si no funciona esta    -  python -m pip install "python-jose[cryptography]" python-multipart python-dotenv
9 . pip install alembic   */Antes de  se verifica que el archivo .env tenga la url correcta con el nombre de la base de datos 
                            junto con la creacion de las tablas , relaciones para evitar fallas .
-- alembic init alembic
-- alembic revision --autogenerate -m "primera migracion"
-- alembic upgrade head
 python seed_admin.py

-- pip install jinja2

uvicorn main:app --reload   /// si hay error por gmaill-   pip install email-validator **// otrra alternativa  uvicorn main:app --reload --port 8001

*/ si hay un error por archivos antiguos  Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

////////////////////////
SENTENCIAS AUXILIARES 
////////////////////////

pip freeze  */Para ver qué librerías tienes instaladas por si se tiene una con una version no deseada 
pip install --no-cache-dir -r requirements.txt  


si por algun motivo no recuerda la contraseña de admi ejecuta en la base de datos esto DELETE FROM usuario WHERE numero_documento = '//aqui va el numero de documento';

.\env\Scripts\activate