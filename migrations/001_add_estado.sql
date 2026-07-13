-- Migration to add 'estado' column to learning tables

-- 1. Table 'rutas'
ALTER TABLE rutas ADD COLUMN estado BOOLEAN NOT NULL DEFAULT TRUE;

-- 2. Table 'tareas'
ALTER TABLE tareas ADD COLUMN estado BOOLEAN NOT NULL DEFAULT TRUE;

-- 3. Table 'guias'
ALTER TABLE guias ADD COLUMN estado BOOLEAN NOT NULL DEFAULT TRUE;
