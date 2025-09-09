-- Cria a tabela quartos caso não exista
CREATE TABLE IF NOT EXISTS quartos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    preco_diaria NUMERIC(10,2) NOT NULL,
    ocupado BOOLEAN DEFAULT FALSE,
    servicos TEXT,
    checkin DATE,
    checkout DATE
);
