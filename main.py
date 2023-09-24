from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
from pymongo import MongoClient

#20 dummy products
products = [
    {"id": 1, "name": "TV", "price": 500.0, "quantity": 100},
    {"id": 2, "name": "Laptop", "price": 1000.0, "quantity": 200},
    {"id": 3, "name": "Smartphone", "price": 300.0, "quantity": 150},
    {"id": 4, "name": "Tablet", "price": 250.0, "quantity": 50},
    {"id": 5, "name": "Headphones", "price": 50.0, "quantity": 300},
    {"id": 6, "name": "Digital Camera", "price": 600.0, "quantity": 75},
    {"id": 7, "name": "Refrigerator", "price": 800.0, "quantity": 120},
    {"id": 8, "name": "Washing Machine", "price": 700.0, "quantity": 100},
    {"id": 9, "name": "Microwave Oven", "price": 150.0, "quantity": 80},
    {"id": 10, "name": "Coffee Maker", "price": 40.0, "quantity": 60},
    {"id": 11, "name": "Blender", "price": 30.0, "quantity": 90},
    {"id": 12, "name": "Toaster", "price": 25.0, "quantity": 70},
    {"id": 13, "name": "Vacuum Cleaner", "price": 120.0, "quantity": 110},
    {"id": 14, "name": "Desk Chair", "price": 80.0, "quantity": 40},
    {"id": 15, "name": "Bookshelf", "price": 45.0, "quantity": 85},
    {"id": 16, "name": "Sofa", "price": 300.0, "quantity": 60},
    {"id": 17, "name": "Dining Table", "price": 200.0, "quantity": 45},
    {"id": 18, "name": "Bed", "price": 400.0, "quantity": 30},
    {"id": 19, "name": "Couch", "price": 350.0, "quantity": 55},
    {"id": 20, "name": "Desk", "price": 75.0, "quantity": 25},
]

def get_product_price(product_id: int) -> float:
    for product in products:
        if product['id'] == product_id:
            return product['price']
    return 0.0

client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB server URL
db = client["ECommerce"]  # Replace with your database name
orders_collection = db["orders"]

app = FastAPI()

#Classes for the different types of data stored

class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

class Address(BaseModel):
    city: str
    country: str
    zip_code: str

class OrderItem(BaseModel):
    product_id: int
    bought_quantity: int

class Order(BaseModel):
    items: List[OrderItem]
    address: Address

class Created_Order(BaseModel):
    id: int
    timestamp: str
    items: List[OrderItem]
    total_amount: float
    address: Address


#API Endpoints

@app.get("/")
async def base():
    return "API is running"

@app.get("/products", response_model=List[Product])
async def get_products():
    return products

@app.post("/orders", response_model=Created_Order)
async def create_order(order: Order):
    totalAmount = 0.0
    for item in order.items:
        price = get_product_price(item.product_id)
        item_price = item.bought_quantity * price
        totalAmount += item_price
    times = datetime.timestamp(datetime.now())
    count = orders_collection.count_documents({})
    created_order = Created_Order(id=(count+1), items=order.items, address=order.address, timestamp=str(times), total_amount=totalAmount)

    # Stores the order in MongoDB
    order_data = created_order.model_dump()
    orders_collection.insert_one(order_data)

    return created_order

@app.get("/orders", response_model=List[Created_Order])
async def get_orders(skip: int = 0, limit: int = 10):
    cursor = orders_collection.find().skip(skip).limit(limit)
    orders_list = [Created_Order(**order) for order in cursor]
    return orders_list

@app.get("/orders/{order_id}", response_model=Created_Order)
async def get_order(order_id: int):
    order_data = orders_collection.find_one({"id": order_id})
    if order_data:
        return Created_Order(**order_data)
    return None

@app.patch("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, quantity: int):
    for index, existing_product in enumerate(products):
        if existing_product["id"] == product_id:
            existing_product["quantity"] = quantity
            products[index] = existing_product
            return existing_product
    raise None





