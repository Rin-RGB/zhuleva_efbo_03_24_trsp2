from fastapi import FastAPI, Query, HTTPException

app = FastAPI()

from db import sample_products

products_db = sample_products
@app.get('/')
async def homepage():
    return {"message": "Поиск по id и ключевому слову. Посмотрите результат по ссылкам:",
            "link1": "http://127.0.0.1:8000/product/123",
            "link2": "http://127.0.0.1:8000/product/search?keyword=phone&category=Electronics&limit=5"}
@app.get('/product/search')
async def search_product(
        keyword: str,
        category: str | None = None,
        limit: int = 10
):
    result = []
    for product in products_db:
        if not (keyword.lower() in product["name"].lower()):
            continue
        if not category or category.lower() == product["category"].lower():
            result.append(product)
        if len(result) >= limit:
            return result
    if not result:
        raise HTTPException(status_code=404, detail=f"Таких продуктов нет")
    return result

@app.get('/product/{product_id}')
async def get_product(product_id: int):
    for product in products_db:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail=f"Продукт с ID {product_id} не найден")
