# Resumen del Proyecto Bit24 Impulsa - Backend API

## 1. Descripción general

Este proyecto es el backend de la plataforma **Bit24 Impulsa**, diseñado para gestionar usuarios, roles, rutas formativas, soporte técnico y progresos en un entorno universitario. Está construido con **FastAPI**, **SQLAlchemy**, **Pydantic** y una base de datos **PostgreSQL**, con una arquitectura modular que separa claramente modelos, esquemas, routers y lógica de seguridad.

## 2. Objetivo del backend

Proveer una API REST segura y estructurada que permita al frontend:
- autenticar usuarios con JWT,
- administrar usuarios y roles,
- validar permisos de acceso,
- consultar el estado de la aplicación y la conexión a la base de datos.

## 3. Componentes principales

### `app/main.py`
- Crea la aplicación FastAPI.
- Configura CORS para el origen `http://localhost:5173`.
- Registra routers: `auth`, `dashboard`, `usuarios` y `roles`.
- Define endpoints de root y health check.

### `app/config.py`
- Carga variables de entorno desde `.env`.
- Define configuración de JWT y la URL de la base de datos.

### `app/database.py`
- Configura SQLAlchemy Engine y `SessionLocal`.
- Proporciona `get_db()` para inyectar la sesión.
- Define la base ORM `Base`.

### `app/core/security.py`
- Implementa el hash de contraseñas con `bcrypt`.
- Genera y valida JWT usando `python-jose`.

### `app/core/dependencies.py`
- Valida el token JWT en cada petición.
- Obtiene el usuario actual desde la base de datos.
- Verifica si el usuario tiene el rol `Administrador`.

### `app/routers/auth.py`
- `POST /auth/login`: autentica usuario y retorna token.
- `GET /auth/me`: devuelve el perfil del usuario autenticado.

### `app/routers/usuarios.py`
- CRUD de usuarios completo.
- Requiere autorización de administrador.
- Usa `UsuarioCreate` y `UsuarioUpdate`.
- Implementa soft delete usando el campo `estado`.

### `app/routers/roles.py`
- `GET /roles`: lista roles.
- Requiere autorización de administrador.

### `app/models/usuarios.py`
- Modelo ORM `Usuario` con campos:
  - `id`, `rol_id`, `nombre`, `apellido`, `correo`, `password_hash`, `estado`, `created_at`.
- Relación con el modelo `Rol`.

### `app/schemas/usuario.py`
- `UsuarioOut`: datos públicos de usuario.
- `UsuarioCreate`: datos requeridos para crear usuario.
- `UsuarioUpdate`: datos opcionales para actualizar.
- `RolOut`: esquema de rol.

## 4. Endpoints disponibles actualmente

- `GET /` : Mensaje de bienvenida.
- `GET /health` : Verifica la conexión con la base de datos.
- `POST /auth/login` : Login por correo y contraseña.
- `GET /auth/me` : Perfil del usuario autenticado.
- `GET /usuarios` : Listar usuarios (admin).
- `GET /usuarios/{usuario_id}` : Obtener usuario por ID (admin).
- `POST /usuarios` : Crear usuario (admin).
- `PUT /usuarios/{usuario_id}` : Actualizar usuario (admin).
- `DELETE /usuarios/{usuario_id}` : Desactivar usuario (admin).
- `GET /roles` : Listar roles (admin).

## 5. Seguridad y permisos

- Autenticación basada en JWT.
- El token se crea en `auth/login` y se valida en `core/dependencies.py`.
- La dependencia `require_admin` solo permite usuarios con rol `Administrador`.
- Los endpoints de usuarios y roles son de uso exclusivo de administradores.

## 6. Estructura de carpetas

```
Bit24ImpulsaBackEnd/
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── .env.example
├── README.md
└── requirements.txt
```

## 7. Dependencias clave

- `fastapi`
- `uvicorn[standard]`
- `sqlalchemy`
- `psycopg2-binary`
- `python-dotenv`
- `pydantic`
- `pydantic-settings`
- `python-jose[cryptography]`
- `bcrypt`
- `python-multipart`
- `email-validator`

## 8. Cómo ejecutar localmente

1. Crear y activar un entorno virtual.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env` y configurar `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM` y `ACCESS_TOKEN_EXPIRE_MINUTES`.
4. Ejecutar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Abrir la documentación en `http://127.0.0.1:8000/docs`.

## 9. Próximas funcionalidades recomendadas

1. Expandir routers y esquemas para los modelos restantes:
   - `actividades`, `alertas`, `categorias_soporte`, `guias`, `integracion_bit24`, `preguntas_ia`, `progreso`, `rutas`, `soporte`, `tareas`.
2. Implementar endpoints CRUD para cada recurso y validar relaciones.
3. Añadir middleware de logs y manejo de errores centralizado.
4. Crear pruebas unitarias y de integración para autenticación y CRUD.
5. Añadir un script de `seed` para roles iniciales y usuarios admin.

## 10. Sugerencia para avanzar

Empieza por los recursos que forman parte del flujo de usuario principal: gestión de rutas, progreso y soporte. Luego agrega control de acceso específico por rol y la documentación de cada endpoint.
