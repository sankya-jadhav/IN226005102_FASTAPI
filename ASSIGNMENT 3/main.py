from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Product Store API - Day 4 Assignment")

# ─── Initial Product Data ─────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook A5", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# ─── Pydantic Model for POST ──────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


@app.get("/products/audit")
def product_audit():
    total_products = len(products)

    in_stock_items = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_items)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    # total_stock_value = sum of (price × 10) for in-stock items only
    total_stock_value = sum(p["price"] * 10 for p in in_stock_items)

    # most_expensive among ALL products
    most_expensive_product = max(products, key=lambda p: p["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        }
    }


@app.put("/products/discount")
def apply_discount(
    category: str = Query(..., description="Category name"),
    discount_percent: int = Query(..., ge=1, le=99, description="Discount percentage (1-99)")
):
    updated_products = []

    for product in products:
        if product["category"].lower() == category.lower():
            old_price = product["price"]
            new_price = int(old_price * (1 - discount_percent / 100))
            product["price"] = new_price
            updated_products.append({
                "name": product["name"],
                "old_price": old_price,
                "new_price": new_price
            })

    if not updated_products:
        return {"message": f"No products found in category '{category}'"}

    return {
        "message": f"{discount_percent}% discount applied to {len(updated_products)} product(s) in '{category}'",
        "updated_products": updated_products
    }


@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail={"error": "Product not found"})


@app.post("/products", status_code=201)
def add_product(product: ProductCreate):
    # Check for duplicate name
    for existing in products:
        if existing["name"].lower() == product.name.lower():
            raise HTTPException(
                status_code=400,
                detail={"error": f"Product with name '{product.name}' already exists"}
            )

    # Auto-generate ID
    new_id = max(p["id"] for p in products) + 1 if products else 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: Optional[str] = Query(None),
    price: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None)
):
    for product in products:
        if product["id"] == product_id:
            if name is not None:
                product["name"] = name
            if price is not None:
                product["price"] = price
            if category is not None:
                product["category"] = category
            if in_stock is not None:
                product["in_stock"] = in_stock
            return {
                "message": "Product updated",
                "product": product
            }

    raise HTTPException(status_code=404, detail={"error": "Product not found"})


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted = products.pop(i)
            return {"message": f"Product '{deleted['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")