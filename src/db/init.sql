CREATE TABLE Secrets (
    key varchar(64) PRIMARY KEY,
    secret_encrypted text,
    passphrase_encrypted text,
    auto_delete_id uuid REFERENCES auto_delete (id),
    is_used boolean NOT NULL DEFAULT false,
    InsDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE auto_delete (
    id uuid not null DEFAULT uuid_generate_v4() PRIMARY KEY,
    delete_name varchar(64),
    InsDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO auto_delete
(delete_name)
VALUES 
('1 hour'),
('5 days'),
('1 min'),
(NULL)
