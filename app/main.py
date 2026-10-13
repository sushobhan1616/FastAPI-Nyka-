from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers.product_router import router as product_router
from app.routers.user_router import router as user_router
from app.routers.cart_router import router as cart_router
from app.routers.order_router import router as order_router

app = FastAPI(title="Nykaa Backend")

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Welcome to Amazon Backend"}


app.include_router(
    product_router,
    prefix="/products",
    tags=["Products"]
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    cart_router,
    prefix="/cart",
    tags=["Cart"]
)

app.include_router(
    order_router,
    prefix="/orders",
    tags=["Orders"]
)
