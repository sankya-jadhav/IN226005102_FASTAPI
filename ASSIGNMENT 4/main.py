from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ================================
# PRODUCT DATABASE
# ================================

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

orders = []
cart = []

# =====================================================
# DAY 1 APIs
# =====================================================

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/category")
def get_products_by_category(category: str):

    result = [p for p in products if p["category"].lower() == category.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"category": category, "products": result, "total": len(result)}


@app.get("/products/in-stock")
def get_in_stock_products():

    result = [p for p in products if p["in_stock"]]

    return {"in_stock_products": result, "count": len(result)}


@app.get("/store/summary")
def store_summary():

    in_stock = len([p for p in products if p["in_stock"]])
    out_stock = len(products) - in_stock
    categories = list(set(p["category"] for p in products))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "categories": categories
    }


@app.get("/products/search")
def search_products(name: str):

    result = [p for p in products if name.lower() in p["name"].lower()]

    if not result:
        return {"message": "No products matched your search"}

    return {"keyword": name, "results": result, "total_matches": len(result)}


@app.get("/products/price-summary")
def price_summary():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {"best_deal": cheapest, "premium_pick": expensive}


# =====================================================
# DAY 2 APIs
# =====================================================

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return {"filtered_products": result}


@app.get("/product/{product_id}/price")
def get_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"price": product["price"]}

    return {"error": "Product not found"}


class Feedback(BaseModel):
    customer_name: str
    product_name: str
    message: str


@app.post("/feedback")
def accept_feedback(feedback: Feedback):

    return {"message": "Feedback received successfully", "data": feedback}


@app.get("/products/dashboard")
def product_dashboard():

    total_products = len(products)

    in_stock = len([p for p in products if p["in_stock"]])
    out_stock = len([p for p in products if not p["in_stock"]])

    avg_price = sum(p["price"] for p in products) / total_products

    return {
        "total_products": total_products,
        "in_stock_products": in_stock,
        "out_of_stock_products": out_stock,
        "average_price": avg_price
    }


class Order(BaseModel):
    product_ids: List[int]


@app.post("/order/bulk")
def place_bulk_order(order: Order):

    valid_products = []
    invalid_products = []

    for pid in order.product_ids:

        product = next((p for p in products if p["id"] == pid), None)

        if not product:
            invalid_products.append({"id": pid, "reason": "Product not found"})

        elif not product["in_stock"]:
            invalid_products.append({"id": pid, "reason": "Out of stock"})

        else:
            valid_products.append(product)

    orders.append(valid_products)

    return {"ordered_products": valid_products, "invalid_products": invalid_products}


# =====================================================
# DAY 3 APIs
# =====================================================

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


@app.post("/products/add")
def add_product(product: NewProduct):

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.put("/products/update/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    return {"error": "Product not found"}


@app.delete("/products/delete/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:
            products.remove(product)
            return {"message": "Product deleted", "product": product}

    return {"error": "Product not found"}


@app.get("/products/audit")
def product_audit():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_names": [p["name"] for p in out_stock],
        "total_stock_value": total_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


@app.put("/products/discount")
def apply_discount(category: str = Query(...), discount_percent: int = Query(..., ge=1, le=90)):

    updated = []

    for product in products:

        if product["category"].lower() == category.lower():

            discount = product["price"] * discount_percent / 100
            product["price"] = int(product["price"] - discount)

            updated.append(product)

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "category": category,
        "discount_percent": discount_percent,
        "updated_products": updated
    }


# =====================================================
# DAY 5 — CART SYSTEM
# =====================================================

@app.post("/cart/add")
def add_to_cart(product_id: int = Query(...), quantity: int = Query(1, gt=0)):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:

        if item["product_id"] == product_id:

            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {"message": "Cart updated", "cart_item": item}

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:

        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Product not in cart")


class CheckoutRequest(BaseModel):

    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    if not cart:

        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    created_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        created_orders.append(order)

        grand_total += item["subtotal"]

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": created_orders,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():

    return {"orders": orders, "total_orders": len(orders)}


# IMPORTANT: Dynamic route LAST
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"message": "Product not found"}