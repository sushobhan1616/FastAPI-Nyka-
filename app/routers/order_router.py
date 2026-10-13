
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.routers.user_router import get_current_user
from app.routers.product_router import products
from app.routers.cart_router import cart_items

router = APIRouter()

orders = []
next_order_id = 1


@router.post("/place")
def place_order(
    current_user: dict = Depends(get_current_user)
):
    global next_order_id

    user_id = current_user["user_id"]

    # Find this customer's cart items
    customer_cart = [
        item for item in cart_items
        if item["user_id"] == user_id
    ]

    if not customer_cart:
        raise HTTPException(
            status_code=400,
            detail="Your cart is empty"
        )

    order_items = []
    total_amount = 0

    # Validate products and stock before creating the order
    for item in customer_cart:
        product_id = item["product_id"]

        if not 0 <= product_id < len(products):
            raise HTTPException(
                status_code=400,
                detail="A product in your cart no longer exists"
            )

        product = products[product_id]
        quantity = item["quantity"]

        if quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )

        subtotal = product.price * quantity
        total_amount += subtotal

        order_items.append({
            "product_id": product_id,
            "product_name": product.name,
            "price": product.price,
            "quantity": quantity,
            "subtotal": round(subtotal, 2)
        })

    # Reduce stock after all items pass validation
    for item in customer_cart:
        products[item["product_id"]].stock -= item["quantity"]

    # Create the order
    new_order = {
        "order_id": next_order_id,
        "user_id": user_id,
        "items": order_items,
        "total_amount": round(total_amount, 2),
        "status": "Placed",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    orders.append(new_order)
    next_order_id += 1

    # Empty only this customer's cart
    cart_items[:] = [
        item for item in cart_items
        if item["user_id"] != user_id
    ]

    return {
        "message": "Order placed successfully",
        "order": new_order
    }


@router.get("/my-orders")
def get_my_orders(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    customer_orders = [
        order for order in orders
        if order["user_id"] == user_id
    ]

    return {
        "user_id": user_id,
        "total_orders": len(customer_orders),
        "orders": customer_orders
    }


@router.get("/details")
def get_order_details(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    for order in orders:
        if (
            order["order_id"] == order_id
            and order["user_id"] == user_id
        ):
            return {"order": order}

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )
