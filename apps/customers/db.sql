-- Crear esquema si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'company') THEN
        EXECUTE 'CREATE SCHEMA company';
    END IF;
END$$;

-- create table if not exists
CREATE TABLE IF NOT EXISTS company.customer (
	id bigserial NOT NULL,
	name varchar(300) NOT NULL,
	email text,
	phone varchar(50),
	cellphone varchar(50),
	country varchar(2), --mx, pl, etc...

	points NUMERIC(10, 2),
	credit NUMERIC(10, 2),

	this_customer_is_a_company boolean NOT NULL DEFAULT false,
	company_name varchar(255),
	contact_name varchar(150),
	contact_email text,
	contact_cellphone varchar(20),
	contact_phone varchar(20),
	website text,
	note text,

	creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_branch bigint,
    
	activated boolean NOT NULL DEFAULT true,
    CONSTRAINT id_key_customer PRIMARY KEY (id)
);


------------------------
CREATE INDEX IF NOT EXISTS idx_customer_name ON company.customer(name);
CREATE INDEX IF NOT EXISTS idx_customer_email ON company.customer(email);
CREATE INDEX IF NOT EXISTS idx_customer_cellphone ON company.customer(cellphone);
CREATE INDEX IF NOT EXISTS idx_customer_id_branch ON company.customer(id_branch);
CREATE INDEX IF NOT EXISTS idx_customer_activated ON company.customer(activated);
CREATE INDEX IF NOT EXISTS idx_customer_company_name ON company.customer(company_name);
CREATE INDEX IF NOT EXISTS idx_customer_email_branch ON company.customer(email, id_branch);




----------------------UPDATES------------------------
