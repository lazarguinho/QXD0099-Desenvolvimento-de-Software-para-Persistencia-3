import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from faker import Faker
import random

# Carregar variáveis de ambiente
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["QXD_Ecommerce"]

faker = Faker()

async def popular_banco():
    print("📢 Populando o banco de dados...")

    # Criar usuários
    users = [{
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
        "address": faker.address(),
        "phoneNumber": faker.phone_number(),
        "carrinho_id": None,
        "pedidos": []
    } for _ in range(25)]
    user_ids = await db.users.insert_many(users)
    
    # Criar categorias
    categories = [{
        "name": faker.word(),
        "description": faker.sentence(),
        "status": random.choice(["ativo", "inativo"]),
        "category_level": random.choice(["baixa", "média", "alta"]),
        "products": []
    } for _ in range(6)]
    category_ids = await db.categories.insert_many(categories)

    # Criar produtos
    products = [{
        "name": faker.word(),
        "description": faker.sentence(),
        "price": round(random.uniform(10, 500), 2),
        "stock_quantity": random.randint(1, 100),
        "category_id": str(random.choice(category_ids.inserted_ids)),
        "carts": [],
        "orders": []
    } for _ in range(25)]
    product_ids = await db.products.insert_many(products)

    # Criar carrinhos
    carts = [{
        "data_criacao": faker.date_time(),
        "subtotal": round(random.uniform(50, 1000), 2),
        "quantidade_items": random.randint(1, 10),
        "status": random.choice(["pendente", "pago", "enviado", "entregue", "cancelado"]),
        "user_id": str(random.choice(user_ids.inserted_ids)),
        "products": [str(random.choice(product_ids.inserted_ids)) for _ in range(random.randint(1, 5))]
    } for _ in range(25)]
    await db.carts.insert_many(carts)

    # Criar pedidos
    orders = [{
        "date": faker.date_time(),
        "status": random.choice(["pendente", "pago", "enviado", "entregue", "cancelado"]),
        "total": round(random.uniform(50, 1000), 2),
        "payment_method": random.choice(["cartão", "boleto", "pix"]),
        "delivery_price": round(random.uniform(5, 50), 2),
        "user_id": str(random.choice(user_ids.inserted_ids)),
        "products": [str(random.choice(product_ids.inserted_ids)) for _ in range(random.randint(1, 5))],
        "reviews": []
    } for _ in range(25)]
    order_ids = await db.orders.insert_many(orders)

    # Criar avaliações
    reviews = [{
        "nota": random.randint(1, 5),
        "comentario": faker.sentence(),
        "data": faker.date_time(),
        "titulo": faker.word(),
        "status": random.choice(["pendente", "aprovado", "rejeitado"]),
        "order_id": str(random.choice(order_ids.inserted_ids))
    } for _ in range(25)]
    await db.reviews.insert_many(reviews)

    print("✅ Banco de dados populado com sucesso!")

if __name__ == "__main__":
    asyncio.run(popular_banco())
