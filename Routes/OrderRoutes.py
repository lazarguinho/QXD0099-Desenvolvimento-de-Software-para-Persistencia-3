from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Order import Order
from typing import List
from bson import ObjectId

order_router = APIRouter()

@order_router.get("/", response_model=List[Order])
async def get_orders(skip: int = 0, limit: int = 10):
    orders = await db.orders.find().skip(skip).limit(limit).to_list(100)
    
    for order in orders:
        order['_id'] = str(order['_id'])
    
    return orders

@order_router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    filt = {"_id": ObjectId(order_id)} if ObjectId.is_valid(order_id) else {"_id": order_id}
    
    order = await db.orders.find_one(filt)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order['_id'] = str(order['_id'])
    
    return order

@order_router.post("/", response_model=Order)
async def create_order(order: Order):
    order_dict = order.model_dump(by_alias=True, exclude={'id'})
    
    new_order = await db.orders.insert_one(order_dict)
    created_order = await db.orders.find_one({"_id": new_order.inserted_id})
    
    if not created_order:
        raise HTTPException(status_code=400, detail="Erro ao criar pedido")
    
    created_order['_id'] = str(created_order['_id'])

    if "products" in order_dict and isinstance(order_dict["products"], list):
        await db.products.update_many(
            {"_id": {"$in": [ObjectId(product_id) for product_id in order_dict["products"]]}},
            {"$addToSet": {"orders": created_order['_id']}}
        )

    if "user_id" in order_dict and order_dict["user_id"]:
        await db.users.update_one(
            {"_id": ObjectId(order_dict["user_id"])},
            {"$addToSet": {"pedidos": created_order['_id']}}
        )

    if "reviews" in order_dict and isinstance(order_dict["reviews"], list):
        await db.reviews.update_many(
            {"_id": {"$in": [ObjectId(review_id) for review_id in order_dict["reviews"]]}},
            {"$set": {"order_id": created_order['_id']}}
        )
    
    return created_order

@order_router.put("/{order_id}", response_model=Order)
async def update_order(order_id: str, order: Order):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order_dict = order.model_dump(by_alias=True, exclude={'id'})
    
    result = await db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": order_dict})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not updated_order:
        raise HTTPException(status_code=400, detail="Erro ao atualizar pedido")
    
    order_id_str = str(updated_order['_id'])

    if "products" in order_dict and isinstance(order_dict["products"], list):
        await db.products.update_many(
            {"_id": {"$in": [ObjectId(product_id) for product_id in order_dict["products"]]}},
            {"$addToSet": {"orders": order_id_str}}
        )

    if "user_id" in order_dict and order_dict["user_id"]:
        await db.users.update_one(
            {"_id": ObjectId(order_dict["user_id"])},
            {"$addToSet": {"pedidos": order_id_str}}
        )

    if "reviews" in order_dict and isinstance(order_dict["reviews"], list):
        await db.reviews.update_many(
            {"_id": {"$in": [ObjectId(review_id) for review_id in order_dict["reviews"]]}},
            {"$set": {"order_id": order_id_str}}
        )
    
    updated_order['_id'] = order_id_str
    
    return updated_order

@order_router.delete("/{order_id}")
async def delete_order(order_id: str):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order_object_id = ObjectId(order_id)
    
    order = await db.orders.find_one({"_id": order_object_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    result = await db.orders.delete_one({"_id": order_object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delete failed")
    
    await db.products.update_many(
        {"orders": order_id},
        {"$pull": {"orders": order_id}}
    )
    
    await db.users.update_many(
        {"pedidos": order_id},
        {"$pull": {"pedidos": order_id}}
    )
    
    await db.reviews.update_many(
        {"order_id": order_id},
        {"$unset": {"order_id": ""}}
    )
    
    return {"message": "Order deleted successfully"}

@order_router.get("/count")
async def get_order_count():
    count = await db.orders.count_documents({})
    return {"total_orders": count}