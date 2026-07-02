# Bit24 Impulsa - Backend API

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D31900?style=for-the-badge)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)

---

## 📌 Descripción del Proyecto

**Bit24 Impulsa** es una plataforma orientada a la gestión de rutas de aprendizaje, tareas y soporte técnico en el contexto de la transformación digital. Este repositorio contiene el **Backend API** del proyecto, desarrollado para un entorno universitario y utilizando el marco de trabajo ágil **Scrum**.

El sistema proporciona endpoints estructurados y seguros para gestionar el progreso de los usuarios, la asignación de rutas formativas, reportes de soporte e integraciones de la plataforma.

---

## 🎯 Objetivo del Backend

El objetivo principal de esta API es servir como una capa intermedia robusta, segura y modular que exponga los servicios necesarios para el cliente (frontend) y coordine la comunicación con la base de datos PostgreSQL. 

Está diseñado bajo una arquitectura limpia con separación de responsabilidades para garantizar la escalabilidad, la protección de recursos mediante roles (Administrador) y la persistencia de datos relacionales en la nube (Supabase).

---

## 🛠️ Arquitectura del Proyecto

El backend está estructurado siguiendo un diseño modular basado en FastAPI. Utiliza una organización por capas que separa:
- **Modelos ORM**: Definición de la estructura de tablas y relaciones de base de datos con SQLAlchemy.
- **Esquemas (Schemas)**: Validaciones de datos de entrada y salida con Pydantic.
- **Rutas (Routers)**: Controladores y endpoints agrupados por recursos.
- **Núcleo (Core)**: Funcionalidades transversales como seguridad (JWT/Bcrypt) y dependencias comunes (inyección de sesiones de DB y validación de roles).

---

## 📂 Estructura de Carpetas

```text
Bit24ImpulsaBackEnd/
│
├── app/
│   ├── core/                  # Seguridad, tokens y dependencias de protección de rutas
│   │   ├── __init__.py
│   │   ├── dependencies.py    # Dependencias comunes (get_db, require_admin, get_current_user)
│   │   └── security.py        # Métodos para token JWT y hashing de contraseñas
│   │
│   ├── models/                # Modelos ORM de SQLAlchemy (Base de datos relacional)
│   │   ├── __init__.py
│   │   ├── actividad.py
│   │   ├── alertas.py
│   │   ├── categorias_soporte.py
│   │   ├── guias.py
│   │   ├── integracion_bit24.py
│   │   ├── preguntas_ia.py
│   │   ├── progreso.py
│   │   ├── roles.py
│   │   ├── rutas.py
│   │   ├── soporte.py
│   │   ├── tareas.py
│   │   └── usuarios.py
│   │
│   ├── routers/               # Controladores y endpoints de la API
│   │   ├── __init__.py
│   │   ├── auth.py            # Endpoints de Login y gestión de sesión (/auth)
│   │   ├── dashboard.py       # Endpoint de estadísticas mock (/dashboard)
│   │   └── usuarios.py        # Endpoints CRUD de usuarios (/usuarios)
│   │
│   ├── schemas/               # Validaciones de entrada/salida de datos (Pydantic)
│   │   ├── __init__.py
│   │   ├── auth.py            # Esquemas para login y respuesta de sesión
│   │   └── usuario.py         # Esquemas CRUD de usuarios (Create, Update, Out)
│   │
│   ├── config.py              # Variables de configuración y lectura de variables de entorno
│   ├── database.py            # Configuración de SQLAlchemy Engine y SessionLocal
│   └── main.py                # Punto de entrada de la aplicación FastAPI
│
├── .env                       # Variables de entorno locales (Excluido en .gitignore)
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Archivos excluidos del control de versiones
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación del proyecto (Este archivo)
```

---

## 💻 Tecnologías Utilizadas

* **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web asíncrono para construir APIs rápidas con Python.
* **[Python 3.11+](https://www.python.org/)**: Lenguaje de programación principal del proyecto.
* **[SQLAlchemy 2.0+](https://www.sqlalchemy.org/)**: ORM de Python para mapear bases de datos relacionales a objetos de Python.
* **[PostgreSQL (Supabase)](https://supabase.com/)**: Motor de base de datos relacional robusto alojado en la nube con Supabase.
* **[Pydantic v2](https://docs.pydantic.dev/)**: Validación de datos estructurados y tipado estático en tiempo de ejecución.
* **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI de alto rendimiento para correr la aplicación FastAPI.
* **[Bcrypt](https://pypi.org/project/bcrypt/)**: Librería nativa para el hasheo seguro de contraseñas.
* **[PyJWT / Python-Jose](https://pypi.org/project/python-jose/)**: Firma y decodificación de tokens JSON Web Tokens (JWT).

---

## 📦 Dependencias del Proyecto

El archivo `requirements.txt` incluye los siguientes paquetes necesarios para la ejecución del servidor:

```text
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-dotenv
pydantic
pydantic-settings
python-jose[cryptography]
bcrypt
python-multipart
email-validator
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/Bit24ImpulsaBackEnd.git
cd Bit24ImpulsaBackEnd
```

### 2. Configuración del Entorno Virtual (Venv)

**En Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
Una vez activado el entorno virtual, instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno (`.env`)

Copia la plantilla `.env.example` para crear tu archivo `.env` de desarrollo local:
```bash
cp .env.example .env
```

Edita el archivo `.env` configurando los parámetros necesarios para conectar tu base de datos y la clave de seguridad del token:

```env
# Database Config (Postgres / Supabase)
# Para desarrollo local (Docker o instalación nativa):
DATABASE_URL=postgresql://postgres:[TU_CONTRASEÑA]@localhost:5432/bit24_impulsa

# Para conexión a Supabase:
# DATABASE_URL=postgresql://postgres.[TU_PROYECTO_ID]:[TU_CONTRASEÑA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require

# JWT Authentication Config
JWT_SECRET=8f9b23b8f10647a7b8e1f0e4b859942d628d08c5c7db81ab9eb56019b8df7907
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🏃 Cómo Ejecutar el Proyecto

Con el entorno virtual activado y las variables de entorno configuradas, inicia el servidor de desarrollo local con `uvicorn`:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📖 Documentación Interactiva (Swagger)

FastAPI genera automáticamente documentación interactiva detallada para probar todos los endpoints disponibles. Con el servidor corriendo, puedes acceder a:

* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Permite realizar peticiones directas desde el navegador).
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (Vista de documentación más limpia y estructurada).

---

## 📊 Estado Actual del Sprint 1

* **Duración**: 2 semanas (Sprint en curso - Día 3-4).
* **Progreso General**: **~20%** de avance estimado.

```text
[████░░░░░░░░░░░░░░░░] 20% Completado
```

### ✅ Funcionalidades Implementadas Hasta el Momento

1. **Diseño de Base de Datos y Modelos ORM**:
   - Creación de modelos de base de datos en SQLAlchemy para los recursos del proyecto: `Usuario`, `Rol`, `Ruta`, `Tarea`, `Progreso`, `Actividad`, `Guia`, `Soporte`, `CategoriasSoporte`, `Alerta`, `PreguntasIA` e `IntegracionBit24`.
2. **Autenticación y Seguridad**:
   - Autenticación mediante JSON Web Tokens (JWT) firmados.
   - Hashing seguro de contraseñas utilizando la librería nativa `bcrypt` (evitando wrappers incompatibles de `passlib`).
   - Endpoints `/auth/login` para generación de tokens de acceso y `/auth/me` para obtener el perfil del usuario autenticado.
3. **Middleware de Control de Acceso (Protección de Roles)**:
   - Dependencia de validación de administrador (`require_admin`) que restringe el acceso solo a usuarios con rol exacto de `"Administrador"`.
4. **CRUD Completo de Usuarios**:
   - Agregados los esquemas Pydantic `UsuarioCreate` y `UsuarioUpdate`.
   - Router `/usuarios` completo con los 5 endpoints CRUD tradicionales (`GET` lista, `GET` detalle, `POST` creación, `PUT` edición y `DELETE` soft delete), todos protegidos con verificación de administrador.
   - Hashing automático de contraseñas en operaciones POST y PUT (si es suministrada).
   - Soft Delete en el endpoint `DELETE` cambiando la propiedad `estado = False` en lugar de borrar físicamente el registro.
5. **Dashboard Base**:
   - Router `/dashboard` para servir métricas estadísticas iniciales mockeadas y lista de notificaciones.

---

### ⏳ Funcionalidades Pendientes (Restante del Sprint 1)

1. **Conexión de Base de Datos Nube (Supabase)**:
   - Despliegue del esquema de tablas directamente a la instancia cloud de Supabase.
   - Inicialización o seeding de roles básicos (`Administrador`, `Usuario`, etc.) en la base de datos real.
2. **Endpoints de Progreso y Aprendizaje**:
   - Creación de routers para la asignación y visualización de rutas de aprendizaje, guías de estudio y tareas asignadas.
3. **Endpoints de Soporte y Alertas**:
   - Controladores para levantar tickets de soporte técnico e interacción con alertas del sistema.
4. **Integraciones Bit24 / Bitrix24**:
   - Configuración de la sincronización de actividades iniciales con la API de Bitrix24.
5. **Pruebas y QA**:
   - Pruebas unitarias de routers clave (Autenticación y CRUD de usuarios).

---

### 🗺️ Roadmap Planificado para el Sprint 1

```mermaid
gantt
    title Roadmap de Desarrollo - Sprint 1
    dateFormat  D
    axisFormat Día %d

    section Inicialización
    Estructura Base y Base de Datos    :active, day1, 3d
    
    section Seguridad y Usuarios
    Autenticación JWT y Rol Admin      :active, day3, 2d
    CRUD Usuarios (Soft Delete)        :active, day4, 1d
    
    section Infraestructura Cloud
    Despliegue y Migración a Supabase :  day5, 2d
    
    section Core de Rutas y Progreso
    Endpoints de Rutas y Tareas        :  day7, 3d
    Endpoints de Soporte y Alertas     :  day10, 2d
    
    section Integración & Cierre
    Integración Inicial con Bit24      :  day11, 2d
    Pruebas Unitarias y QA             :  day13, 1d
    Cierre de Sprint y Demo            :  day14, 1d
```

---

## 📜 Convenciones del Proyecto

* **Formateo de Código**: Todo el código debe adherirse a la guía de estilo **PEP 8**.
* **Validación de Datos**: Las peticiones de entrada y respuestas de salida deben tiparse rigurosamente utilizando esquemas de **Pydantic**.
* **Borrado Lógico**: No se permite la eliminación directa de registros en la base de datos (`DELETE` físico), en su lugar se debe implementar **Soft Delete** cambiando el estado del registro a `False`/`inactivo` (ej. `estado = False` en `Usuario`).
* **Seguridad de Endpoints**: Todos los endpoints de gestión administrativa deben inyectar la dependencia `require_admin` para evitar el acceso no autorizado.

---

## 📄 Licencia

Este proyecto es desarrollado con fines estrictamente académicos para la universidad. El código fuente es de uso privado en el ámbito educativo.

---
📄 *Desarrollado bajo el marco ágil de Scrum - 2026.*
