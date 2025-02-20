from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Category import Category
from typing import List
from bson import ObjectId

category_router = APIRouter()


@category_router.get("/", response_model=List[Category])
async def get_categories(skip: int = 0, limit: int = 10):
	categories = await db.categories.find().skip(skip).limit(limit).to_list(100)

	for category in categories:
		category['_id'] = str(category['_id'])

	return categories

@category_router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
	filt = {"_id": ObjectId(category_id)} if ObjectId.is_valid(category_id) else {"_id": category_id}

	category = await db.categories.find_one(filt)

	if not category:
		raise HTTPException(status_code=404, detail="Category not found")

	category['_id'] = str(category['_id'])

	return category

@category_router.post("/", response_model=Category)
async def create_category(category: Category):
    category_dict = category.model_dump(by_alias=True, exclude={'id'})

    new_category = await db.categories.insert_one(category_dict)    
    created_category = await db.categories.find_one({"_id": new_category.inserted_id})

    if not created_category:
        raise HTTPException(status_code=400, detail="Erro ao criar categoria")

    category_id_str = str(created_category['_id'])

    # Se houver produtos associados, adicionar o ID da categoria à lista de categorias de cada produto
    if "products" in category_dict and isinstance(category_dict["products"], list):
        await db.products.update_many(
            {"_id": {"$in": [ObjectId(product_id) for product_id in category_dict["products"]]}},
            {"$set": {"category_id": category_id_str}}
        )

    created_category['_id'] = category_id_str

    return created_category


@category_router.put("/{category_id}", response_model=Category)
async def update_category(category_id: str, category: Category):
	if not ObjectId.is_valid(category_id):
		raise HTTPException(status_code=400, detail="Invalid category ID")

	category_dict = category.model_dump(by_alias=True, exclude={'id'})

	result = await db.categories.update_one({"_id": ObjectId(category_id)}, {"$set": category_dict})

	if result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Category not found")

	updated_category = await db.categories.find_one({"_id": ObjectId(category_id)})

	if not updated_category:
		raise HTTPException(status_code=400, detail="Erro ao atualizar categoria")
	
	if "products" in category_dict and isinstance(category_dict["products"], list):
		await db.products.update_many(
			{"_id": {"$in": [ObjectId(product_id) for product_id in category_dict["products"]]}},
			{"$set": {"category_id": category_id}}
		)

	updated_category['_id'] = str(updated_category['_id'])

	return updated_category

@category_router.delete("/{category_id}")
async def delete_category(category_id: str):
	if not ObjectId.is_valid(category_id):
		raise HTTPException(status_code=400, detail="Invalid category ID")
	
	category_object_id = ObjectId(category_id)

	category = await db.categories.find_one({"_id": category_object_id})

	if not category:
		raise HTTPException(status_code=404, detail="Category not found")
	
	result = await db.categories.delete_one({"_id": category_object_id})

	if result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Delete failed")
	
	await db.products.update_many(
		{"category_id": category_id},
		{"$unset": {"category_id": ""}}
	)

	return {"message": "Category deleted successfully"}	

@category_router.get("/count")
async def get_category_count():
	count = await db.categories.count_documents({})
	return {"total_categories": count}