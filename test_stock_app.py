from pathlib import Path

import pytest

from stock_app import InventoryManager


def _manager(tmp_path: Path) -> InventoryManager:
    return InventoryManager(data_file=str(tmp_path / "inventory.json"))


def test_add_and_get_product(tmp_path: Path) -> None:
    manager = _manager(tmp_path)

    manager.add_product("SKU-001", "Clavier", 10, 3, 49.99)
    product = manager.get_product("SKU-001")

    assert product is not None
    assert product.name == "Clavier"
    assert product.quantity == 10


def test_prevent_duplicate_sku(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.add_product("SKU-001", "Clavier", 10, 3, 49.99)

    with pytest.raises(ValueError):
        manager.add_product("SKU-001", "Souris", 10, 2, 19.99)


def test_update_stock(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.add_product("SKU-001", "Clavier", 10, 3, 49.99)

    manager.update_stock("SKU-001", -2)

    assert manager.get_product("SKU-001").quantity == 8


def test_cannot_go_negative(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.add_product("SKU-001", "Clavier", 1, 1, 49.99)

    with pytest.raises(ValueError):
        manager.update_stock("SKU-001", -2)


def test_low_stock_products(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.add_product("SKU-001", "Clavier", 2, 3, 49.99)
    manager.add_product("SKU-002", "Souris", 8, 3, 19.99)

    low_stock = manager.low_stock_products()

    assert len(low_stock) == 1
    assert low_stock[0].sku == "SKU-001"


def test_inventory_value(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.add_product("SKU-001", "Clavier", 2, 3, 10)
    manager.add_product("SKU-002", "Souris", 3, 1, 5)

    assert manager.inventory_value() == 35
