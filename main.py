import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.usuario import router as usuario_router
from routes.coordinacion import router as coordinacion_router
from routes.programa import router as programa_router
from routes.proyecto import router as proyecto_router
from routes.ficha import router as ficha_router
from routes.competencia import router as competencia_router
from routes.materiales import router as materiales_router
from routes.nota import router as nota_router
from routes.rol import router as rol_router
from routes.instructor import router as instructor_router
from api.v1 import auth

from db.database import engine, Base
# Se importa el paquete "models" completo (no un modelo suelto) para que
# TODOS los modelos queden registrados en Base.metadata ANTES de llamar a
# create_all(). Antes esto funcionaba "por casualidad" porque los routers
# importados arriba, de forma indirecta, ya cargaban cada modelo -- pero
# dependía del orden de imports y no era explícito. Con este import queda
# garantizado sin importar qué se reordene en el futuro.
import models  # noqa: F401

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Repositorio SENA", version="1.0.0")

# ==========================================================================
# 1. CONTROL DE RED (CORS) - Opcional
# ==========================================================================
# El login (templates/login.html + static/js/auth.js) lo sirve esta MISMA
# API con Jinja2, así que navegador y servidor comparten origen y el
# navegador NUNCA bloquea esas peticiones: no hace falta CORS para que tu
# login funcione. Por eso ya no es obligatorio configurar ALLOWED_ORIGINS
# para poder arrancar el servidor.
#
# Solo lo necesitarías si en el futuro separas el frontend a otro dominio
# o puerto (por ejemplo, una app en React corriendo con "npm start" en
# localhost:3000, aparte de este servidor). En ese caso, define
# ALLOWED_ORIGINS en el .env (ej: ALLOWED_ORIGINS=http://localhost:3000)
# y este bloque lo activa automáticamente.
origins_raw = os.getenv("ALLOWED_ORIGINS")
if origins_raw:
    LISTA_ORIGENES = [origen.strip() for origen in origins_raw.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LISTA_ORIGENES,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )


# ==========================================================================
# 2. CABECERAS DE SEGURIDAD (Anti-Clickjacking / Anti-Sniffing de tipo MIME)
# ==========================================================================
@app.middleware("http")
async def añadir_cabeceras_seguridad(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Las vistas de sesión no deben quedar almacenadas para que el navegador
    # las restaure al usar Atrás/Adelante.
    if request.url.path in {"/login", "/dashboard", "/instructor"}:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


# ==========================================================================
# 3. RUTAS DE LA API
# ==========================================================================
app.include_router(usuario_router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(coordinacion_router, prefix="/api/coordinaciones", tags=["Coordinaciones"])
app.include_router(programa_router, prefix="/api/programas", tags=["Programas"])
app.include_router(proyecto_router, prefix="/api/proyectos", tags=["Proyectos"])
app.include_router(ficha_router, prefix="/api/fichas", tags=["Fichas"])
app.include_router(competencia_router, prefix="/api/competencias", tags=["Competencias"])
app.include_router(materiales_router, prefix="/api/materiales", tags=["Materiales"])
app.include_router(nota_router, prefix="/api/notas", tags=["Notas"])
app.include_router(rol_router, prefix="/api/roles", tags=["Roles"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(instructor_router, prefix="/api/instructores", tags=["Instructor"])


# ==========================================================================
# 4. FRONTEND (HTML servido por la misma API, mismo origen -> sin CORS)
# ==========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/login")


@app.get("/login")
async def pagina_login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/dashboard")
async def pagina_dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/instructor")
async def pagina_instructor(request: Request):
    return templates.TemplateResponse(request, "instructor.html")


@app.get("/instructor/competencias")
async def pagina_instructor_competencias(request: Request):
    # Misma SPA del instructor, iniciando directamente en Competencias.
    return templates.TemplateResponse(request, "instructor.html")


@app.get("/api")
async def api_status():
    return {"message": "Servidor del repositorio SENA corriendo"}


def custom_openapi():
    """Configura Swagger para aceptar tokens JWT y mostrar el candado."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API Proyecto VICTORIA",
        version="1.0.0",
        description="Sistema de gestión académica y roles",
        routes=app.routes,
    )

    # Define cómo se ve el botón de autorización
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Pega aquí tu token JWT.",
        }
    }

    # Le pone candado a TODAS las rutas, EXCEPTO a las de registro y login
    for path, path_item in openapi_schema.get("paths", {}).items():
        if path.startswith("/api") and "/auth" not in path:
            for method, operation in path_item.items():
                operation["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Activamos la personalización de Swagger
app.openapi = custom_openapi
