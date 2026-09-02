# VICTORIA — API + Login ensamblados

## Qué se hizo

Se unió tu API (FastAPI) con el diseño HTML del login en un solo proyecto,
en esta misma carpeta. La página de login ya no simula el ingreso: llama
de verdad a tu API y consulta tu base de datos.

Cambios concretos:

- `main.py`: ahora también sirve el frontend (monta `/static` y las
  plantillas Jinja2). Como el HTML se sirve desde el mismo servidor que
  la API, **no hay problema de CORS** para el login.
- `templates/login.html`: el formulario ya no hace un submit normal;
  usa JavaScript (`static/js/auth.js`) para mandar tus credenciales a
  `POST /api/v1/auth/login`, recibe el token JWT real y lo guarda en
  `sessionStorage`.
- `templates/dashboard.html` (nuevo): página simple que, apenas cargas,
  llama a `GET /api/v1/auth/me` con el token y pinta en pantalla los
  datos reales del usuario que inició sesión (nombre, documento,
  correos, estado, rol) — todo consultado en vivo contra la base de
  datos, nada de datos de ejemplo.
- `api/v1/auth.py`: se agregó el endpoint `GET /api/v1/auth/me`
  (no existía) porque el dashboard lo necesita para leer el perfil del
  usuario autenticado.
- `requirements.txt`: se agregó `Jinja2` (necesario para renderizar las
  plantillas HTML) y se limpió la codificación del archivo.

## Cómo correrlo

1. Activa tu entorno virtual e instala dependencias:
   ```
   pip install -r requirements.txt
   ```
2. Revisa tu `.env` (ya está con tu configuración de Postgres):
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:postgresql@127.0.0.1:5432/VICTORIAA
   ```
   Ajusta usuario/contraseña/puerto si tu Postgres local es distinto.
3. Levanta el servidor:
   ```
   uvicorn main:app --reload
   ```
4. Abre en el navegador:
   ```
   http://127.0.0.1:8000/login
   ```
   (la raíz `/` redirige automáticamente a `/login`)

## Cómo probarlo con un usuario real

Si aún no tienes usuarios en la tabla `usuario`, regístrate primero desde
Swagger (`http://127.0.0.1:8000/docs` → `POST /api/v1/auth/register`) o
con `seed_admin.py`. **Importante:** para poder registrar un usuario debe
existir antes una fila en la tabla `rol` con `nombre_rol = 'aprendiz'`
(es el rol por defecto que usa el registro público).

Luego en `/login` ingresas el **número de documento** (no el correo) y
la contraseña. Si son correctos, te lleva a `/dashboard` con tus datos
reales.

## Notas de seguridad que ya traía tu API (se respetaron)

- Contraseñas con hash PBKDF2, nunca en texto plano.
- JWT firmado con tu `SECRET_KEY`, expira según `ACCESS_TOKEN_EXPIRE_MINUTES`.
- CORS con lista blanca (`ALLOWED_ORIGINS`) — solo importa si en el futuro
  separas el frontend a otro dominio/puerto; sirviendo todo junto como
  quedó aquí, no aplica.
- El registro público nunca deja que el cliente se autoasigne un rol.
