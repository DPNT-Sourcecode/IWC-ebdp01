from dataclasses import dataclass

@dataclass
class InventoryItem:
    sku: str
    name: str
    price: int
