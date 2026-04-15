-- =============================================
-- Practice 8 - PostgreSQL Procedures for PhoneBook
-- =============================================

-- Create table if it does not exist.
CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_first_name UNIQUE (first_name)
);

-- Table to store invalid bulk import rows.
CREATE TABLE IF NOT EXISTS invalid_contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    phone VARCHAR(30),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Procedure 1:
-- Insert user or update phone if user already exists.
CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_first_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE first_name = p_first_name;
    ELSE
        INSERT INTO phonebook(first_name, phone)
        VALUES (p_first_name, p_phone);
    END IF;
END;
$$;

-- Procedure 2:
-- Insert many users from arrays.
-- Uses loop + IF validation.
-- Incorrect data is stored in invalid_contacts.
CREATE OR REPLACE PROCEDURE bulk_upsert_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    current_name TEXT;
    current_phone TEXT;
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have the same length';
    END IF;

    FOR i IN 1..COALESCE(array_length(p_names, 1), 0) LOOP
        current_name := trim(p_names[i]);
        current_phone := trim(p_phones[i]);

        -- Validation: name cannot be empty and phone must contain only digits,
        -- optional +, spaces and dashes. Must also contain at least 6 digits.
        IF current_name IS NULL OR current_name = '' THEN
            INSERT INTO invalid_contacts(first_name, phone, reason)
            VALUES (current_name, current_phone, 'Empty name');
        ELSIF current_phone IS NULL OR current_phone = '' THEN
            INSERT INTO invalid_contacts(first_name, phone, reason)
            VALUES (current_name, current_phone, 'Empty phone');
        ELSIF current_phone !~ '^\\+?[0-9 -]+$' THEN
            INSERT INTO invalid_contacts(first_name, phone, reason)
            VALUES (current_name, current_phone, 'Phone contains invalid characters');
        ELSIF length(regexp_replace(current_phone, '\\D', '', 'g')) < 6 THEN
            INSERT INTO invalid_contacts(first_name, phone, reason)
            VALUES (current_name, current_phone, 'Phone is too short');
        ELSE
            CALL upsert_contact(current_name, current_phone);
        END IF;
    END LOOP;
END;
$$;

-- Procedure 3:
-- Delete contact by username(first_name) or phone.
CREATE OR REPLACE PROCEDURE delete_contact(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = p_value OR phone = p_value;
END;
$$;
