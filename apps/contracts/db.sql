-- SQL statements for database setup go here
-- Create schema if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'contracts') THEN
        EXECUTE 'CREATE SCHEMA contracts';
    END IF;
END$$;

-- Create table if not exists
CREATE TABLE IF NOT EXISTS contracts.contract (
    id bigserial NOT NULL,
    user_id bigint NOT NULL,
    title varchar(300) NOT NULL,
    description text,
    content_html text,
    active boolean NOT NULL DEFAULT true,
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_contract PRIMARY KEY (id)
);

-- Add foreign key if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'user_fk'
          AND table_schema = 'contracts'
          AND table_name = 'contract'
    ) THEN
        ALTER TABLE contracts.contract
        ADD CONSTRAINT user_fk FOREIGN KEY (user_id)
        REFERENCES public.users (id)
        MATCH FULL
        ON DELETE CASCADE
        ON UPDATE CASCADE;
    END IF;
END$$;
