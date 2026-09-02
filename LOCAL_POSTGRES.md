# VICTORIA en un computador nuevo: PostgreSQL + Instructor

## 1. Instalar PostgreSQL

Instala PostgreSQL con **pgAdmin 4**. Durante la instalación recuerda el usuario y contraseña que elegiste para PostgreSQL.

## 2. Crear la base de datos

En pgAdmin:

1. Abre **Servers > PostgreSQL > Databases**.
2. Clic derecho en **Databases > Create > Database...**.
3. Nombre: `victoria`.
4. Guarda.

La configuración del proyecto debe apuntar a esa base en `VICTORIA/.env` mediante `DATABASE_URL`.

## 3. Crear las tablas

Abre PowerShell dentro de:

```text
victoria_final/VICTORIA
```

Activa tu entorno virtual e instala dependencias:

```powershell
pip install -r requirements.txt
```

Luego ejecuta una vez:

```powershell
python -c "from db.database import Base, engine; import models; Base.metadata.create_all(bind=engine); print('Tablas creadas')"
```

El proyecto usa SQLAlchemy y las tablas se crean desde los modelos.

También existe `scriptposgrest`, que contiene el esquema SQL original del proyecto.

## 4. Crear los roles y un instructor

Ejecuta:

```powershell
python seed_instructor.py
```

El programa te pedirá los datos del instructor y creará el rol `instructor` si no existe.

## 5. Levantar VICTORIA

```powershell
python -m uvicorn main:app --reload
```

Abre:

```text
http://127.0.0.1:8000/login
```

Ingresa el **número de documento** y la contraseña del instructor.

VICTORIA consultará el usuario en PostgreSQL, validará la contraseña con PBKDF2 y, si el rol es `instructor`, abrirá `/instructor`.

## 6. Ver la base de datos

En pgAdmin:

```text
Servers
└── PostgreSQL
    └── Databases
        └── victoria
            └── Schemas
                └── public
                    └── Tables
```

Busca la tabla `usuario`.

Para verla: clic derecho sobre `usuario` → **View/Edit Data > All Rows**.

Ahí podrás comprobar que el instructor realmente quedó guardado.

## 7. Comprobar el login desde Swagger

Con el servidor encendido abre:

```text
http://127.0.0.1:8000/docs
```

Busca:

```text
POST /api/v1/auth/login
```

El campo `username` corresponde al **número de documento**.

Después puedes probar:

```text
GET /api/v1/auth/me
```

La respuesta debe mostrar `rol_nombre: "instructor"`.
