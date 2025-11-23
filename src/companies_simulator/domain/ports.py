from typing import Protocol, List, Optional
from companies_simulator.domain.models import Company, Product, PricingState, AnnualMetrics


class RepositoryPort(Protocol):
    """Puerto (interface) para acceso a persistencia."""

    def list_companies(self) -> List[Company]:
        ...

    def get_company(self, company_id: int) -> Optional[Company]:
        ...

    def list_products(self, company_id: int) -> List[Product]:
        ...

    def get_pricing_state(self, product_id: int) -> Optional[PricingState]:
        ...

    def upsert_pricing_state(self, pricing: PricingState) -> PricingState:
        ...

    def get_annual_metrics(self, product_id: int, year: int) -> Optional[AnnualMetrics]:
        ...

    def list_annual_metrics(self, product_id: int) -> List[AnnualMetrics]:
        ...

    def upsert_annual_metrics(self, metrics: AnnualMetrics) -> AnnualMetrics:
        ...
