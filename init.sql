CREATE TABLE IF NOT EXISTS cliente (
    id_cliente SERIAL PRIMARY KEY,
    login_cliente VARCHAR(100) NOT NULL UNIQUE,
    nome_cliente VARCHAR(200) NOT NULL,
    senha_hash VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS vendedor (
    id_vendedor SERIAL PRIMARY KEY,
    login_vendedor VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(200) NOT NULL,
    nome_vendedor VARCHAR(200) NOT NULL
);

-- Cria a tabela quartos caso não exista
CREATE TABLE IF NOT EXISTS quartos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    preco_diaria NUMERIC(10,2) NOT NULL,
    ocupado BOOLEAN DEFAULT FALSE,
    status_quarto VARCHAR(20) NOT NULL,
    servicos TEXT,
    checkin DATE,
    checkout DATE,
    vendedor_id INT NOT NULL,
    CONSTRAINT fk_vendedor_quarto FOREIGN KEY (vendedor_id) REFERENCES vendedor(id_vendedor) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva SERIAL PRIMARY KEY,
    id_quarto INT NOT NULL,
    id_cliente INT NOT NULL,
    data_checkin DATE NOT NULL,
    data_checkout DATE NOT NULL,
    pago BOOLEAN DEFAULT FALSE,
    autorizado BOOLEAN DEFAULT FALSE,
    autorizado_por INT,            -- vendedor que autorizou (nullable até autorizar)
    autorizado_em TIMESTAMP,       -- quando foi autorizado
    CONSTRAINT fk_quarto_reserva FOREIGN KEY (id_quarto) REFERENCES quartos(id) ON DELETE CASCADE,
    CONSTRAINT fk_cliente_reserva FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    CONSTRAINT fk_vendedor_autorizador FOREIGN KEY (autorizado_por) REFERENCES vendedor(id_vendedor) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_reserva_id_quarto ON reserva(id_quarto);
CREATE INDEX IF NOT EXISTS idx_reserva_id_cliente ON reserva(id_cliente);

CREATE OR REPLACE VIEW reservas_detalhes AS
SELECT 
    r.id_reserva,
    c.nome_cliente,
    q.codigo AS codigo_quarto,
    q.tipo AS tipo_quarto,
    q.preco_diaria,
    r.data_checkin,
    r.data_checkout,
    r.pago,
    r.autorizado,
    v.nome_vendedor AS autorizado_por,
    r.autorizado_em,
    CASE 
        WHEN CURRENT_DATE BETWEEN r.data_checkin AND r.data_checkout 
            THEN 'Indisponível'
        ELSE 'Disponível'
    END AS status_reserva
FROM reserva r
JOIN cliente c ON r.id_cliente = c.id_cliente
JOIN quartos q ON r.id_quarto = q.id
LEFT JOIN vendedor v ON r.autorizado_por = v.id_vendedor;



