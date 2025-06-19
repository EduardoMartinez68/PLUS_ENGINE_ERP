-- Crear esquema si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'company') THEN
        EXECUTE 'CREATE SCHEMA company';
    END IF;
END$$;

-- Crear tabla company.company si no existe
CREATE TABLE IF NOT EXISTS company.company (
    id bigserial NOT NULL,
    name varchar(300),
    CONSTRAINT id_key_company PRIMARY KEY (id)
);

-- Crear tabla company.branch si no existe
CREATE TABLE IF NOT EXISTS company.branch (
    id bigserial NOT NULL,
    id_company bigint,
    CONSTRAINT id_key_branch PRIMARY KEY (id)
);

-- Agregar FK de branch -> company
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'company_fk'
          AND table_schema = 'company'
          AND table_name = 'branch'
    ) THEN
        ALTER TABLE company.branch
        ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
        REFERENCES company.company (id)
        MATCH FULL
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END$$;

-- Crear tabla public.users si no existe
CREATE TABLE IF NOT EXISTS public.users (
    id bigserial NOT NULL PRIMARY KEY,
    path_photo text,
    username varchar(600) NOT NULL,
    email varchar(254) NOT NULL UNIQUE,
    password varchar(128) NOT NULL,  -- Django usa hasta 128 caracteres para el hash de password
    id_company bigint,
    id_branch bigint,
    is_active boolean NOT NULL DEFAULT true,
    is_staff boolean NOT NULL DEFAULT false,
    is_superuser boolean NOT NULL DEFAULT false,
    last_login timestamp with time zone,
    date_joined timestamp with time zone NOT NULL DEFAULT now()
);

-- Agregar FK de users -> company
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'company_fk'
          AND table_schema = 'public'
          AND table_name = 'users'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
        REFERENCES company.company (id)
        MATCH FULL
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END$$;

-- Agregar FK de users -> branch
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'branch_fk'
          AND table_schema = 'public'
          AND table_name = 'users'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT branch_fk FOREIGN KEY (id_branch)
        REFERENCES company.branch (id)
        MATCH FULL
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END$$;
