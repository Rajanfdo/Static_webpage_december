from fastapi import FastAPI
from database import Base, engine  
from routers import (
    admin , login, users, address, categories,
    fishes, orders, order_items, order_tracking, reviews
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FishStore API")




app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(login.router, prefix="/api/login", tags=["login"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(address.router, prefix="/api/address", tags=["address"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(fishes.router, prefix="/api/fishes", tags=["fishes"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["order-items"])
app.include_router(order_tracking.router, prefix="/api/order-tracking", tags=["order-tracking"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])




    


