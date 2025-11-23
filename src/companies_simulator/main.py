"""CLI de demostración para Companies Simulator"""
import os
import argparse
from decimal import Decimal

from companies_simulator.adapters.postgres_repository import PostgresRepository
from companies_simulator.services.pricing_service import PricingService


def list_companies(repo: PostgresRepository):
    for c in repo.list_companies():
        print(f"{c.id}: {c.name} ({c.created_at})")


def list_products(repo: PostgresRepository, company_id: int):
    for p in repo.list_products(company_id):
        print(f"{p.id}: {p.name} sku={p.sku} cost={p.marginal_cost}")


def show_pricing(repo: PostgresRepository, product_id: int):
    s = repo.get_pricing_state(product_id)
    if not s:
        print("No pricing state found")
        return
    print(s)


def set_price(repo: PostgresRepository, product_id: int, price: Decimal):
    service = PricingService(repo)
    updated = service.set_price(product_id, price)
    print("Updated:", updated)


def main():
    parser = argparse.ArgumentParser(description="Companies Simulator CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list-companies")
    p = sub.add_parser("list-products")
    p.add_argument("--company-id", type=int, required=True)

    sp = sub.add_parser("show-pricing")
    sp.add_argument("--product-id", type=int, required=True)

    pp = sub.add_parser("set-price")
    pp.add_argument("--product-id", type=int, required=True)
    pp.add_argument("--price", required=True)

    args = parser.parse_args()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Set DATABASE_URL environment variable (e.g. postgresql+psycopg2://user:pass@host:port/db)")
        return

    repo = PostgresRepository(db_url)

    if args.cmd == "list-companies":
        list_companies(repo)
    elif args.cmd == "list-products":
        list_products(repo, args.company_id)
    elif args.cmd == "show-pricing":
        show_pricing(repo, args.product_id)
    elif args.cmd == "set-price":
        price = Decimal(args.price)
        set_price(repo, args.product_id, price)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
