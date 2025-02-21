from Config.config import db
from fastapi import APIRouter, HTTPException


other_router = APIRouter()


@other_router.get("/count-all")
async def count_all():
    total_entities = sum([
        await db.users.count_documents({}),
        await db.reviews.count_documents({}),
        await db.products.count_documents({}),
        await db.orders.count_documents({}),
        await db.categories.count_documents({}),
        await db.carts.count_documents({})
    ])

    return {"total_entities": total_entities}
