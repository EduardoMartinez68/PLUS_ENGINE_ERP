CREATE TABLE IF NOT EXISTS documentos_relacionados (
  id SERIAL PRIMARY KEY,
  caso_id INTEGER NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  contenido TEXT,

  CONSTRAINT fk_caso
    FOREIGN KEY (caso_id)
    REFERENCES casos(id)
    ON DELETE CASCADE
);
