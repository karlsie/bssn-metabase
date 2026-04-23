from fastapi import FastAPI
import random
from datetime import datetime
import json

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


with open("/app/data/nilai_csm.json") as f:
    nilai_csm_data = json.load(f)

with open("/app/data/stakeholder.json") as f:
    stakeholder_data = json.load(f)


@app.get("/orders")
def get_orders(limit: int = 10, page: int = 1):

    data = []
    for i in range(limit):
        data.append(
            {
                "order_id": page * 1000 + i,
                "amount": round(random.uniform(10, 500), 2),
                "created_at": datetime.utcnow().isoformat(),
                "status": random.choice(["new", "processing", "completed"]),
            }
        )

    return {
        "message": "true",
        "status": "success",
        "data": data,
    }


@app.get("/nilai_csm")
def get_nilai_csm():
    return {"message": "true", "status": "success", "data": nilai_csm_data}


@app.get("/stakeholder")
def get_stakeholder():
    return {"message": "true", "status": "success", "data": stakeholder_data}
