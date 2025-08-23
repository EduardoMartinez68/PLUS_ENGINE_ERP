-- create schema if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'company') THEN
        EXECUTE 'CREATE SCHEMA company';
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'erp') THEN
        EXECUTE 'CREATE SCHEMA erp';
    END IF;
END$$;

--create table company.company if not exists
CREATE TABLE IF NOT EXISTS company.company (
	id bigserial NOT NULL,
	company_name varchar(300),
	name_of_the_person_in_charge varchar(150) NOT NULL,
	email_of_the_person_in_charge text NOT NULL,
	creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT id_key_company PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_company_email ON company.company(email_of_the_person_in_charge);
CREATE INDEX IF NOT EXISTS idx_company_name ON company.company(company_name);

---------------------------------------------------------------------------------------------
-- create table company.branch when not exist
CREATE TABLE IF NOT EXISTS company.branch (
	id bigserial NOT NULL,
	id_company bigint,
	name_branch varchar(500) NOT NULL,
	nickname varchar(100),
	email_branch text,
	country varchar(2),
	address text,
	postal_code varchar(10),
	cellphone varchar(25),
	phone varchar(25),
	website text,
	name_of_the_person_in_charge text,
	email_of_the_person_in_charge text,

    ---data of the information in google---
	user_google text,
	password_google text

    --
	creation_date date NOT NULL DEFAULT CURRENT_TIMESTAMP,
	activated boolean NOT NULL DEFAULT true,
	CONSTRAINT id_key_branch PRIMARY KEY (id),

	CONSTRAINT company_fk FOREIGN KEY (id_company)
		REFERENCES company.company (id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_branch_id_company ON company.branch(id_company);
CREATE INDEX IF NOT EXISTS idx_branch_email ON company.branch(email_branch);
CREATE INDEX IF NOT EXISTS idx_branch_name ON company.branch(name_branch);



----------------------------------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS company.user_type (
	id bigserial NOT NULL,
	name varchar(100) NOT NULL,
	description text,
	id_company bigint,
	activated boolean NOT NULL DEFAULT true,
	CONSTRAINT id_key_user_type PRIMARY KEY (id),

	CONSTRAINT fk_user_type_company FOREIGN KEY (id_company)
		REFERENCES company.company(id)
		ON DELETE SET NULL

);
CREATE INDEX IF NOT EXISTS idx_user_type_name ON company.user_type(name);
CREATE INDEX IF NOT EXISTS idx_user_type_id_company ON company.user_type(id_company);


---------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS company.permits(
	id bigserial NOT NULL,
	id_company bigint,
	name varchar(100) NOT NULL,
	description text,
	creation_date timestamp DEFAULT CURRENT_TIMESTAMP,
	activated boolean NOT NULL DEFAULT true,
	view_permits boolean DEFAULT true,
	edit_permits boolean NOT NULL DEFAULT true,
	delete_permits boolean NOT NULL DEFAULT true,
	CONSTRAINT id_key_permits PRIMARY KEY (id),

	CONSTRAINT fk_permits_company FOREIGN KEY (id_company)
		REFERENCES company.company(id)
		ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_permits_name ON company.permits(name);
CREATE INDEX IF NOT EXISTS idx_permits_id_company ON company.permits(id_company);


---------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS company.users (
	id bigserial PRIMARY KEY,

    path_photo text,
	name varchar(600) NOT NULL,
	email text NOT NULL,
	password text NOT NULL,

	cellphone varchar(20),
	phone varchar(20),
	address text,
	country varchar(2),
	postal_code varchar(20),
	date_of_birth date,
	hiring_date date,

	id_permits bigint,
	id_user_type bigint,

	creation_date timestamp DEFAULT CURRENT_TIMESTAMP,
	activated boolean NOT NULL DEFAULT true,
	id_company bigint NOT NULL,
	id_branch bigint NOT NULL,



	CONSTRAINT fk_employees_company FOREIGN KEY (id_company)
		REFERENCES company.company(id)
		ON DELETE CASCADE,

	CONSTRAINT fk_employees_branch FOREIGN KEY (id_branch)
		REFERENCES company.branch(id)
		ON DELETE CASCADE,

	CONSTRAINT fk_employees_permits FOREIGN KEY (id_permits)
		REFERENCES company.permits(id)
		ON DELETE SET NULL,

	CONSTRAINT fk_employees_user_type FOREIGN KEY (id_user_type)
		REFERENCES company.user_type(id)
		ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_employees_id_company ON branch.employees(id_company);
CREATE INDEX IF NOT EXISTS idx_employees_id_branch ON branch.employees(id_branch);
CREATE INDEX IF NOT EXISTS idx_employees_email ON branch.employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_name ON branch.employees(name);
CREATE INDEX IF NOT EXISTS idx_employees_user_type ON branch.employees(id_user_type);
CREATE INDEX IF NOT EXISTS idx_employees_permits ON branch.employees(id_permits);




---------------------------------SETTING OF THE ERP-------------------------------
CREATE TABLE IF NOT EXISTS erp.setting(
	id bigserial NOT NULL,
    ---styles of the ERP---
	company_color varchar(7) NOT NULL DEFAULT #075FAF,
	secondary_color varchar(7) NOT NULL DEFAULT #074c8dff,
	button_color varchar(7) NOT NULL DEFAULT #075FAF,
	button_success varchar(7) NOT NULL DEFAULT #075FAF,
	currency_type varchar(5) NOT NULL DEFAULT MXN,


	CONSTRAINT id_key_setting_erp PRIMARY KEY (id)
);