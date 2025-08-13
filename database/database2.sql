-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.7.0
-- PostgreSQL version: 9.3
-- Project Site: pgmodeler.com.br
-- Model Author: ---

SET check_function_bodies = false;
-- ddl-end --


-- Database creation must be done outside an multicommand file.
-- These commands were put in this file only for convenience.
-- -- object: new_database | type: DATABASE --
-- -- DROP DATABASE new_database;
-- CREATE DATABASE new_database
-- ;
-- -- ddl-end --
-- 

-- object: erp | type: SCHEMA --
-- DROP SCHEMA erp;
CREATE SCHEMA IF NOT EXISTS erp;
-- ddl-end --

SET search_path TO pg_catalog,public,company,branch,cases,customer,erp;
-- ddl-end --

-- object: public.branch | type: SEQUENCE --
-- DROP SEQUENCE public.branch;
CREATE SEQUENCE IF NOT EXISTS erp.branch_id_seq
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE
    OWNED BY erp.branch.id;
-- ddl-end --

-- object: branch.employees | type: TABLE --
-- DROP TABLE branch.employees;
CREATE TABLE IF NOT EXISTS branch.employees (
	id bigserial PRIMARY KEY,

	-- User information
	id_company bigint,
	id_branch bigint,
	photo_path text,
	user_name VARCHAR(50) NOT NULL,
	email text NOT NULL,
	password text NOT NULL,

	-- Personal information
	name varchar(100) NOT NULL,
	cellphone varchar(20),
	phone varchar(20),
	address text,
	country varchar(2),  -- ISO country code (e.g., MX, PL, US)
	postal_code varchar(20),

	-- Employee information
	date_of_birth date,
	hiring_date date,
	salary NUMERIC(10,2),
	purchase_discount_percent NUMERIC(5,2),  -- Discount on purchases
	sales_commission_percent NUMERIC(5,2),   -- Commission per sale
	id_permits bigint,
	id_user_type bigint,

	-- Metadata
	creation_date timestamp DEFAULT CURRENT_TIMESTAMP,
	is_active boolean NOT NULL DEFAULT true
);

-- ddl-end --
-- object: company.company | type: TABLE --
-- DROP TABLE company.company;
CREATE TABLE IF NOT EXISTS company.company (
    id BIGSERIAL PRIMARY KEY,

    -- General information
    logo_path TEXT,
    company_name VARCHAR(300) NOT NULL,            -- Legal or trade name
    tax_identifier VARCHAR(50),                    -- RFC (MX), NIP (PL), VAT ID, etc.
    company_type VARCHAR(50),                      -- Legal type: 'LLC', 'S.A. de C.V.', 'Sp. z o.o.', etc.

    -- Location and contact
    country VARCHAR(2),                            -- ISO 3166-1 alpha-2 (e.g., 'MX', 'PL')
    fiscal_address TEXT,    
    company_phone VARCHAR(20),
    company_email VARCHAR(150),
    website TEXT,

    -- Representative / owner
    person_in_charge_name VARCHAR(150) NOT NULL,
    person_in_charge_email TEXT NOT NULL,
    person_in_charge_phone VARCHAR(20),

    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE IF NOT EXISTS INDEX idx_company_country ON company.company(country);
CREATE IF NOT EXISTS INDEX idx_company_name ON company.company(company_name);

-- ddl-end --
-- object: company.branch | type: TABLE --
-- DROP TABLE company.branch;
CREATE TABLE IF NOT EXISTS company.branch (
    id BIGSERIAL PRIMARY KEY,

    id_company BIGINT NOT NULL,
    branch_name VARCHAR(500) NOT NULL,
    nickname VARCHAR(100),
    email TEXT,
    country VARCHAR(2),  -- ISO 3166-1 alpha-2
    address TEXT,
    postal_code VARCHAR(10),
    cellphone VARCHAR(25),
    phone VARCHAR(25),
    website TEXT,

    name_of_the_person_in_charge TEXT,
    email_of_the_person_in_charge TEXT,

    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_company FOREIGN KEY (id_company) REFERENCES company.company(id)
);

-- ddl-end --
-- object: company_fk | type: CONSTRAINT --
-- ALTER TABLE company.branch DROP CONSTRAINT company_fk;
ALTER TABLE company.branch ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
REFERENCES company.company (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: company_fk | type: CONSTRAINT --
-- ALTER TABLE branch.employees DROP CONSTRAINT company_fk;
ALTER TABLE branch.employees ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
REFERENCES company.company (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: branch_fk | type: CONSTRAINT --
-- ALTER TABLE branch.employees DROP CONSTRAINT branch_fk;
ALTER TABLE branch.employees ADD CONSTRAINT branch_fk FOREIGN KEY (id_branch)
REFERENCES company.branch (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: customer.customer | type: TABLE --
-- DROP TABLE customer.customer;
CREATE TABLE IF NOT EXISTS customer.customer (
    id BIGSERIAL PRIMARY KEY,

    id_branch BIGINT,

    -- Basic Information 
    name VARCHAR(300) NOT NULL,
    email TEXT,
    phone VARCHAR(50),
    cellphone VARCHAR(50),

    -- Loyalty and Credit Program Information
    points INTEGER DEFAULT 0,
    credit INTEGER DEFAULT 0,

    country VARCHAR(2), -- ISO 3166-1 alpha-2 code (e.g., 'MX', 'PL')

    -- Company Customer Information
    this_customer_is_a_company BOOLEAN NOT NULL DEFAULT FALSE,
    company_name VARCHAR(255),
    contact_name VARCHAR(150),
    contact_email TEXT,
    contact_cellphone VARCHAR(20),
    contact_phone VARCHAR(20),
    website TEXT,

    -- Notes and Metadata
    note TEXT,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- ddl-end --
-- object: branch_fk | type: CONSTRAINT --
-- ALTER TABLE customer.customer DROP CONSTRAINT branch_fk;
ALTER TABLE customer.customer ADD CONSTRAINT branch_fk FOREIGN KEY (id_branch)
REFERENCES company.branch (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: company.permits | type: TABLE --
-- DROP TABLE company.permits;
CREATE TABLE IF NOT EXISTS company.permits (
    id BIGSERIAL PRIMARY KEY,

    id_company BIGINT,

    name VARCHAR(100) NOT NULL,
    description TEXT,

    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Basic permissions flags
    this_is_admin BOOLEAN DEFAULT TRUE,
    can_view BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN NOT NULL DEFAULT TRUE,
    can_delete BOOLEAN NOT NULL DEFAULT TRUE

    -- Additional permissions to be added later by apps/modules
);

-- ddl-end --
-- object: company_fk | type: CONSTRAINT --
-- ALTER TABLE company.permits DROP CONSTRAINT company_fk;
ALTER TABLE company.permits ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
REFERENCES company.company (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: company.user_type | type: TABLE --
-- DROP TABLE company.user_type;
CREATE TABLE IF NOT EXISTS company.user_type (
    id BIGSERIAL PRIMARY KEY,

    id_company BIGINT,

    name VARCHAR(100) NOT NULL,
    description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- ddl-end --
-- object: permits_fk | type: CONSTRAINT --
-- ALTER TABLE branch.employees DROP CONSTRAINT permits_fk;
ALTER TABLE branch.employees ADD CONSTRAINT permits_fk FOREIGN KEY (id_permits)
REFERENCES company.permits (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: user_type_fk | type: CONSTRAINT --
-- ALTER TABLE branch.employees DROP CONSTRAINT user_type_fk;
ALTER TABLE branch.employees ADD CONSTRAINT user_type_fk FOREIGN KEY (id_user_type)
REFERENCES company.user_type (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: company_fk | type: CONSTRAINT --
-- ALTER TABLE company.user_type DROP CONSTRAINT company_fk;
ALTER TABLE company.user_type ADD CONSTRAINT company_fk FOREIGN KEY (id_company)
REFERENCES company.company (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


-- object: erp.setting | type: TABLE --
-- DROP TABLE erp.setting;
CREATE TABLE IF NOT EXISTS erp.setting (
    id BIGSERIAL PRIMARY KEY,

    company_color VARCHAR(7) NOT NULL DEFAULT '#075FAF',
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#074C8D',
    button_color VARCHAR(7) NOT NULL DEFAULT '#075FAF',
    button_success VARCHAR(7) NOT NULL DEFAULT '#075FAF',

    currency_type VARCHAR(5) NOT NULL DEFAULT 'MXN'
);

-- ddl-end --

