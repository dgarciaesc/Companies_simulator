-- Schema para Companies Simulator

CREATE TABLE company (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    current_turn INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    company_id      BIGINT REFERENCES company(id),
    is_admin        BOOLEAN DEFAULT FALSE,
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
    price           NUMERIC(12,4),
    items_sold      INTEGER DEFAULT 0,
    marginal_cost   NUMERIC(12,4),
    created_at      TIMESTAMPTZ DEFAULT now(),

    UNIQUE (product_id, year)
);

CREATE INDEX idx_pam_product ON product_annual_metrics(product_id);
CREATE INDEX idx_pam_year ON product_annual_metrics(year);

-- Marketing budget and metrics tables
CREATE TABLE company_marketing_state (
    id                      BIGSERIAL PRIMARY KEY,
    company_id              BIGINT NOT NULL UNIQUE REFERENCES company(id),
    current_budget_spent    NUMERIC(18,4) DEFAULT 0,
    current_brand_perception NUMERIC(8,4) DEFAULT 0.5,
    last_update_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_cms_company ON company_marketing_state(company_id);

CREATE TABLE company_marketing_annual (
    id              BIGSERIAL PRIMARY KEY,
    company_id      BIGINT NOT NULL REFERENCES company(id),
    year            INTEGER NOT NULL,
    budget_spent    NUMERIC(18,4) NOT NULL DEFAULT 0,
    brand_perception NUMERIC(8,4) DEFAULT 0.5,
    created_at      TIMESTAMPTZ DEFAULT now(),

    UNIQUE (company_id, year)
);

CREATE INDEX idx_cma_company ON company_marketing_annual(company_id);
CREATE INDEX idx_cma_year ON company_marketing_annual(year);

-- Finance annual metrics table for balance sheet data
CREATE TABLE company_finance_annual (
    id                      BIGSERIAL PRIMARY KEY,
    company_id              BIGINT NOT NULL REFERENCES company(id),
    fiscal_year             INTEGER NOT NULL,
    
    -- Revenue and costs
    revenue                 NUMERIC(18,4) NOT NULL DEFAULT 0,
    operational_costs       NUMERIC(18,4) NOT NULL DEFAULT 0,
    fabrication_costs       NUMERIC(18,4) NOT NULL DEFAULT 0,
    
    -- Assets
    inventory_value         NUMERIC(18,4) NOT NULL DEFAULT 0,
    other_assets            NUMERIC(18,4) NOT NULL DEFAULT 0,
    total_assets            NUMERIC(18,4) NOT NULL DEFAULT 0,
    
    -- Debt and amortization
    total_debt              NUMERIC(18,4) NOT NULL DEFAULT 0,
    amortization            NUMERIC(18,4) NOT NULL DEFAULT 0,
    
    -- Profitability metrics
    ebit                    NUMERIC(18,4) NOT NULL DEFAULT 0,
    ebitda                  NUMERIC(18,4) NOT NULL DEFAULT 0,
    free_cash_flow          NUMERIC(18,4) NOT NULL DEFAULT 0,
    
    created_at              TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE (company_id, fiscal_year)
);

CREATE INDEX idx_cfa_company ON company_finance_annual(company_id);
CREATE INDEX idx_cfa_fiscal_year ON company_finance_annual(fiscal_year);

