from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Review import Review
from typing import List
from bson import ObjectId

review_router = APIRouter()

from datetime import datetime
from fastapi import Query

@review_router.get("/", response_model=List[Review])
async def get_reviews(
    skip: int = 0, 
    limit: int = 10, 
    year: int = Query(None, description="Filtrar avaliações por ano"),
    start_date: str = Query(None, description="Filtrar avaliações a partir de uma data (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Filtrar avaliações até uma data (YYYY-MM-DD)")
):
    query = {}

    # Filtrar por ano (extrai avaliações dentro do ano específico)
    if year:
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        query["data"] = {"$gte": start, "$lte": end}

    # Filtrar por intervalo de datas (separado do filtro de ano)
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query["data"] = {"$gte": start, "$lte": end}
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")
    
    reviews = await db.reviews.find(query).skip(skip).limit(limit).to_list(100)

    for review in reviews:
        review['_id'] = str(review['_id'])

    return reviews


@review_router.get("/{review_id}", response_model=Review)
async def get_review(review_id: str):
    filt = {"_id": ObjectId(review_id)} if ObjectId.is_valid(review_id) else {"_id": review_id}

    review = await db.reviews.find_one(filt)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review['_id'] = str(review['_id'])

    return review

@review_router.post("/", response_model=Review)
async def create_review(review: Review):
    review_dict = review.model_dump(by_alias=True, exclude={'id'})

    new_review = await db.reviews.insert_one(review_dict)
    created_review = await db.reviews.find_one({"_id": new_review.inserted_id})

    if not created_review:
        raise HTTPException(status_code=400, detail="Erro ao criar review")

    created_review['_id'] = str(created_review['_id'])

    return created_review

@review_router.put("/{review_id}", response_model=Review)
async def update_review(review_id: str, review: Review):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID")
    
    review_dict = review.model_dump(by_alias=True, exclude={'id'})

    result = await db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": review_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")

    updated_review = await db.reviews.find_one({"_id": ObjectId(review_id)})

    if not updated_review:
        raise HTTPException(status_code=400, detail="Erro ao atualizar review")

    updated_review['_id'] = str(updated_review['_id'])

    return updated_review

@review_router.delete("/{review_id}")
async def delete_review(review_id: str):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review_object_id = ObjectId(review_id)

    review = await db.reviews.find_one({"_id": review_object_id})

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    result = await db.reviews.delete_one({"_id": review_object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delete failed")

    return {"message": "Review deleted successfully"}

@review_router.get("/count")
async def get_review_count():
    count = await db.reviews.count_documents({})
    return {"total_reviews": count}