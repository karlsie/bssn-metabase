from fastapi import FastAPI
from typing import List
import random
from datetime import datetime

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders")
def get_orders(limit: int = 10, page: int = 1):

    data = []
    for i in range(limit):
        data.append({
            "order_id": page * 1000 + i,
            "amount": round(random.uniform(10, 500), 2),
            "created_at": datetime.utcnow().isoformat(),
            "status": random.choice(["new", "processing", "completed"])
        })

    return {
        "page": page,
        "limit": limit,
        "results": data,
        "next": True if page < 5 else False
    }
