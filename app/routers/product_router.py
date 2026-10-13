from fastapi import APIRouter
from pydantic import BaseModel, field_validator

router = APIRouter()

products = []


class Product(BaseModel):
    name: str
    description: str
    price: float
    category: str
    brand: str
    stock: int

    @field_validator("stock")
    def stock_must_be_non_negative(cls, value):
        if value < 0:
            raise ValueError("Stock must be non-negative")
        return value


# CREATE PRODUCT
@router.post("/create")
def create_product(product: Product):

    products.append(product)

    return {
        "message": "Product created successfully",
        "product": product
    }


# GET ALL PRODUCTS
@router.get("/all")
def get_products():

    return {
        "products": products
    }


# GET ONE PRODUCT
@router.get("/get")
def get_product(product_id: int):

    return {
        "product_id": product_id,
        "product": products[product_id]
    }


# UPDATE PRODUCT
@router.put("/update")
def update_product(product_id: int, product: Product):
    
    products[product_id] = product

    return {
        "message": "Product updated successfully",
        "product_id": product_id,
        "product": product
    }


# DELETE PRODUCT
@router.delete("/delete")
def delete_product(product_id: int):

    deleted_product = products.pop(product_id)

    return {
        "message": "Product deleted successfully",
        "product": deleted_product
    }