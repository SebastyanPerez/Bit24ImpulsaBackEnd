-- Migration to create indexes on foreign keys to optimize joins and queries in the Dashboard
-- Created on: 2026-07-16

-- 1. Table 'usuarios'
CREATE INDEX IF NOT EXISTS idx_usuarios_rol_id ON usuarios(rol_id);

-- 2. Table 'rutas'
CREATE INDEX IF NOT EXISTS idx_rutas_rol_id ON rutas(rol_id);

-- 3. Table 'tareas'
CREATE INDEX IF NOT EXISTS idx_tareas_ruta_id ON tareas(ruta_id);

-- 4. Table 'progreso'
CREATE INDEX IF NOT EXISTS idx_progreso_usuario_id ON progreso(usuario_id);
CREATE INDEX IF NOT EXISTS idx_progreso_tarea_id ON progreso(tarea_id);
CREATE INDEX IF NOT EXISTS idx_progreso_usuario_tarea ON progreso(usuario_id, tarea_id);

-- 5. Table 'actividad'
CREATE INDEX IF NOT EXISTS idx_actividad_usuario_id ON actividad(usuario_id);

-- 6. Table 'alertas'
CREATE INDEX IF NOT EXISTS idx_alertas_usuario_id ON alertas(usuario_id);

-- 7. Table 'soporte'
CREATE INDEX IF NOT EXISTS idx_soporte_usuario_id ON soporte(usuario_id);
CREATE INDEX IF NOT EXISTS idx_soporte_responsable_id ON soporte(responsable_id);
CREATE INDEX IF NOT EXISTS idx_soporte_categoria_id ON soporte(categoria_id);
