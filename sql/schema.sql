-- Schema para Companies Simulator

CREATE TABLE company (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    company_id      BIGINT REFERENCES company(id),
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE product (
    id                  BIGSERIAL PRIMARY KEY,
    company_id          BIGINT NOT NULL REFERENCES company(id),
    name                TEXT NOT NULL,
    sku                 TEXT,
    marginal_cost       NUMERIC(12,4) NOT NULL,
    market_perception   TEXT,
    additional_info     TEXT,
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_product_company ON product(company_id);

CREATE TABLE product_pricing_state (
    id                   BIGSERIAL PRIMARY KEY,
    product_id           BIGINT NOT NULL REFERENCES product(id),

    current_price        NUMERIC(12,4) NOT NULL,
    current_demand       NUMERIC(18,4),
    current_market_share NUMERIC(8,4),

    price_elasticity     NUMERIC(8,4) NOT NULL,
    last_update_at       TIMESTAMPTZ DEFAULT now(),

    UNIQUE (product_id)
);

CREATE INDEX idx_pps_product ON product_pricing_state(product_id);

CREATE TABLE product_annual_metrics (
    id              BIGSERIAL PRIMARY KEY,
    product_id      BIGINT NOT NULL REFERENCES product(id),
    year            INTEGER NOT NULL,
    revenue         NUMERIC(18,4) NOT NULL,
    market_share    NUMERIC(8,4),
    demand          NUMERIC(18,4),
    created_at      TIMESTAMPTZ DEFAULT now(),

    UNIQUE (product_id, year)
);

CREATE INDEX idx_pam_product ON product_annual_metrics(product_id);
CREATE INDEX idx_pam_year ON product_annual_metrics(year);
