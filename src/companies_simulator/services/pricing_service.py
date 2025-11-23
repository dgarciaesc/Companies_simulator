from decimal import Decimal
from typing import Optional
from companies_simulator.domain.ports import RepositoryPort
from companies_simulator.domain.models import PricingState


class PricingService:
    """Casos de uso relacionados con pricing."""

    def __init__(self, repo: RepositoryPort):
        self.repo = repo

    def set_price(self, product_id: int, price: Decimal) -> PricingState:
        state = self.repo.get_pricing_state(product_id)
        if not state:
            # If no state exists, create minimal default with elasticity -1.0
            state = PricingState(id=None, product_id=product_id, current_price=price, current_demand=None, current_market_share=None, price_elasticity=Decimal("-1.0"))
        else:
            state.current_price = price

        updated = self.repo.upsert_pricing_state(state)
        return updated

    def increase_price_by_pct(self, product_id: int, pct: Decimal) -> PricingState:
        state = self.repo.get_pricing_state(product_id)
        if not state:
            raise ValueError("Pricing state not found for product")
        new_price = state.current_price * (Decimal("1.0") + pct)
        state.current_price = new_price
        return self.repo.upsert_pricing_state(state)
