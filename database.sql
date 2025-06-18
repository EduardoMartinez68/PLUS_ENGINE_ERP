CREATE TABLE IF NOT EXISTS permisos (
  id SERIAL PRIMARY KEY,
  clave TEXT UNIQUE NOT NULL,
  descripcion TEXT
);