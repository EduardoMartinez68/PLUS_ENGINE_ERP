-- Crear esquema si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'customer') THEN
        EXECUTE 'CREATE SCHEMA customer';
    END IF;
END$$;

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS customer.customer (
    id bigserial NOT NULL,
    id_branch bigint,
    name varchar(300) NOT NULL,
    email text,
    this_customer_is_a_company boolean NOT NULL DEFAULT false,
    company_name varchar(255),
    rfc varchar(50),
    curp varchar(50),
    phone varchar(50),
    cellphone varchar(50),
    website text,
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    country varchar(100),
    status boolean NOT NULL DEFAULT true,
    CONSTRAINT id_key_customer PRIMARY KEY (id)
);

-- Agregar la FK solo si no existe (esto es más elegante)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'branch_fk'
          AND table_schema = 'customer'
          AND table_name = 'customer'
    ) THEN
        ALTER TABLE customer.customer
        ADD CONSTRAINT branch_fk FOREIGN KEY (id_branch)
        REFERENCES company.branch (id)
        MATCH FULL
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END$$;
