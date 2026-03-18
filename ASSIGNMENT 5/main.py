from fastapi import FastAPI, Query

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []


@app.post("/orders")
def place_order(customer_name: str, product_id: int, quantity: int = 1):
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    order = {
        "order_id": len(orders) + 1,
        "customer_name": customer_name,
        "product": product["name"],
        "quantity": quantity,
        "total_price": product["price"] * quantity,
        "status": "pending"
    }

    orders.append(order)
    return {"message": "Order placed successfully", "order": order}


# Q1 — Search products
@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [p for p in products if keyword.lower() in p["name"].lower()]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# Q2 — Sort products
@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    result = sorted(products, key=lambda p: p[sort_by], reverse=(order == "desc"))

    return {
        "sort_by": sort_by,
        "order": order,
        "products": result
    }


# Q3 — Pagination
@app.get("/products/page")
def get_products_page(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):
    start = (page - 1) * limit
    total_pages = -(-len(products) // limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": total_pages,
        "products": products[start:start + limit]
    }


# Q4 — Search orders
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# Q5 — Sort by category then price
@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))

    return {
        "products": result,
        "total": len(result)
    }


# Q6 — Browse: search + sort + paginate
@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20),
):
    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))

    total = len(result)
    total_pages = -(-total // limit) if total > 0 else 0
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": paged
    }


# Bonus — Orders pagination
@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit) if len(orders) > 0 else 0,
        "orders": orders[start:start + limit],
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"message": "Product not found"}