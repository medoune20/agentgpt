from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Product:
    sku: str
    name: str
    quantity: int
    min_quantity: int
    unit_price: float


class InventoryManager:
    def __init__(self, data_file: str = "inventory.json") -> None:
        self.data_path = Path(data_file)
        self.products: Dict[str, Product] = {}
        self._load()

    def _load(self) -> None:
        if not self.data_path.exists():
            return

        raw_data = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.products = {
            item["sku"]: Product(**item)
            for item in raw_data.get("products", [])
        }

    def save(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "products": [asdict(product) for product in self.products.values()],
        }
        self.data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_product(
        self,
        sku: str,
        name: str,
        quantity: int,
        min_quantity: int,
        unit_price: float,
    ) -> Product:
        if sku in self.products:
            raise ValueError(f"Le SKU '{sku}' existe déjà.")
        if quantity < 0 or min_quantity < 0 or unit_price < 0:
            raise ValueError("Les valeurs numériques doivent être positives.")

        product = Product(
            sku=sku,
            name=name,
            quantity=quantity,
            min_quantity=min_quantity,
            unit_price=unit_price,
        )
        self.products[sku] = product
        self.save()
        return product

    def update_stock(self, sku: str, delta: int) -> Product:
        product = self._get_product_or_raise(sku)
        new_quantity = product.quantity + delta
        if new_quantity < 0:
            raise ValueError("Le stock ne peut pas être négatif.")

        product.quantity = new_quantity
        self.save()
        return product

    def update_product(
        self,
        sku: str,
        *,
        name: Optional[str] = None,
        min_quantity: Optional[int] = None,
        unit_price: Optional[float] = None,
    ) -> Product:
        product = self._get_product_or_raise(sku)

        if name is not None:
            product.name = name
        if min_quantity is not None:
            if min_quantity < 0:
                raise ValueError("Le seuil minimum doit être positif.")
            product.min_quantity = min_quantity
        if unit_price is not None:
            if unit_price < 0:
                raise ValueError("Le prix doit être positif.")
            product.unit_price = unit_price

        self.save()
        return product

    def delete_product(self, sku: str) -> None:
        self._get_product_or_raise(sku)
        del self.products[sku]
        self.save()

    def get_product(self, sku: str) -> Optional[Product]:
        return self.products.get(sku)

    def list_products(self) -> List[Product]:
        return sorted(self.products.values(), key=lambda p: p.sku)

    def low_stock_products(self) -> List[Product]:
        return sorted(
            [p for p in self.products.values() if p.quantity <= p.min_quantity],
            key=lambda p: p.sku,
        )

    def inventory_value(self) -> float:
        return sum(p.quantity * p.unit_price for p in self.products.values())

    def _get_product_or_raise(self, sku: str) -> Product:
        product = self.get_product(sku)
        if product is None:
            raise KeyError(f"Produit avec SKU '{sku}' introuvable.")
        return product


def _prompt(message: str) -> str:
    return input(message).strip()


def _print_menu() -> None:
    print("\n=== Gestion de stock ===")
    print("1. Ajouter un produit")
    print("2. Mettre à jour le stock")
    print("3. Modifier un produit")
    print("4. Supprimer un produit")
    print("5. Afficher les produits")
    print("6. Produits en stock faible")
    print("7. Valeur totale du stock")
    print("0. Quitter")


def _display_products(products: List[Product]) -> None:
    if not products:
        print("Aucun produit.")
        return

    print("\nSKU | Nom | Qté | Min | Prix")
    print("-" * 50)
    for p in products:
        print(f"{p.sku} | {p.name} | {p.quantity} | {p.min_quantity} | {p.unit_price:.2f} €")


def run_cli() -> None:
    manager = InventoryManager()

    actions = {
        "1": lambda: manager.add_product(
            sku=_prompt("SKU: "),
            name=_prompt("Nom: "),
            quantity=int(_prompt("Quantité initiale: ")),
            min_quantity=int(_prompt("Seuil minimum: ")),
            unit_price=float(_prompt("Prix unitaire (€): ")),
        ),
        "2": lambda: manager.update_stock(
            sku=_prompt("SKU: "),
            delta=int(_prompt("Variation de stock (+/-): ")),
        ),
        "3": lambda: manager.update_product(
            sku=_prompt("SKU: "),
            name=_prompt("Nouveau nom (laisser vide pour ignorer): ") or None,
            min_quantity=(
                int(value)
                if (value := _prompt("Nouveau seuil min (laisser vide pour ignorer): "))
                else None
            ),
            unit_price=(
                float(value)
                if (value := _prompt("Nouveau prix (laisser vide pour ignorer): "))
                else None
            ),
        ),
        "4": lambda: manager.delete_product(_prompt("SKU: ")),
        "5": lambda: _display_products(manager.list_products()),
        "6": lambda: _display_products(manager.low_stock_products()),
        "7": lambda: print(f"Valeur totale: {manager.inventory_value():.2f} €"),
    }

    while True:
        _print_menu()
        choice = _prompt("Votre choix: ")

        if choice == "0":
            print("Au revoir !")
            break

        action = actions.get(choice)
        if not action:
            print("Choix invalide.")
            continue

        try:
            result = action()
            if isinstance(result, Product):
                print(f"Opération réussie pour le produit {result.sku}.")
            elif result is None and choice in {"1", "2", "3", "4"}:
                print("Opération réussie.")
        except Exception as exc:  # noqa: BLE001
            print(f"Erreur: {exc}")


if __name__ == "__main__":
    run_cli()
