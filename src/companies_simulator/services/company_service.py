from dataclasses import asdict
from decimal import Decimal
from typing import List, Optional
from companies_simulator.domain.models import Company, Product, AnnualMetrics
from companies_simulator.domain.ports import RepositoryPort


class CompanyService:
    """Service for company-related operations."""
    
    def __init__(self, repository: RepositoryPort):
        self.repository = repository
    
    def get_all_companies(self) -> List[Company]:
        """Get all companies."""
        return self.repository.list_companies()
    
    def get_company(self, company_id: int) -> Optional[Company]:
        """Get a specific company by ID."""
        return self.repository.get_company(company_id)
    
    def get_company_products(self, company_id: int) -> List[Product]:
        """Get all products for a company."""
        return self.repository.list_products(company_id)
    
    def get_product_metrics(self, product_id: int) -> List[AnnualMetrics]:
        """Get historical annual metrics for a product."""
        return self.repository.list_annual_metrics(product_id)
    
    def get_product_metrics_by_year(self, product_id: int, year: int) -> Optional[AnnualMetrics]:
        """Get metrics for a specific product and year."""
        return self.repository.get_annual_metrics(product_id, year)
