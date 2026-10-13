
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.routers.user_router import get_current_user
from app.routers.product_router import products

router = APIRouter()

# Temporary storage for cart items
cart_items = []


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


@router.post("/add")
def add_to_cart(
    item: CartItem,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    # Check whether the product exists
    if not 0 <= item.product_id < len(products):
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[item.product_id]

    # Check stock availability
    if item.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # Check whether this product is already in this user's cart
    for cart_item in cart_items:
        if (
            cart_item["user_id"] == user_id
            and cart_item["product_id"] == item.product_id
        ):
            new_quantity = cart_item["quantity"] + item.quantity

            if new_quantity > product.stock:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough stock for requested quantity"
                )

            cart_item["quantity"] = new_quantity
            return {
                "message": "Cart quantity updated",
                "product_id": item.product_id,
                "quantity": new_quantity
            }

    # Add a new item to the cart
    new_item = {
        "user_id": user_id,
        "product_id": item.product_id,
        "quantity": item.quantity
    }

    cart_items.append(new_item)

    return {
        "message": "Product added to cart",
        "product_id": item.product_id,
        "quantity": item.quantity
    }


@router.get("/")
def view_cart(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    result = []
    total_price = 0

    for item in cart_items:
        if item["user_id"] == user_id:
            product_id = item["product_id"]

            # Ignore stale product references if products were deleted
            if not 0 <= product_id < len(products):
                continue

            product = products[product_id]
            subtotal = product.price * item["quantity"]
            total_price += subtotal

            result.append({
                "product_id": product_id,
                "name": product.name,
                "price": product.price,
                "quantity": item["quantity"],
                "subtotal": subtotal
            })

    return {
        "user_id": user_id,
        "items": result,
        "total_price": round(total_price, 2)
    }


@router.put("/update")
def update_cart_item(
    item: CartItem,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    if not 0 <= item.product_id < len(products):
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[item.product_id]

    if item.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Not enough stock")

    for cart_item in cart_items:
        if (
            cart_item["user_id"] == user_id
            and cart_item["product_id"] == item.product_id
        ):
            cart_item["quantity"] = item.quantity
            return {
                "message": "Cart updated successfully",
                "product_id": item.product_id,
                "quantity": item.quantity
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in your cart"
    )


@router.delete("/remove")
def remove_from_cart(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    for index, item in enumerate(cart_items):
        if (
            item["user_id"] == user_id
            and item["product_id"] == product_id
        ):
            cart_items.pop(index)
            return {
                "message": "Product removed from cart",
                "product_id": product_id
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in your cart"
    )


@router.delete("/clear")
def clear_cart(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    cart_items[:] = [
        item for item in cart_items
        if item["user_id"] != user_id
    ]

    return {"message": "Your cart has been cleared"}
