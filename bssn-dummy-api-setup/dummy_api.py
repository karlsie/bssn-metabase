from fastapi import FastAPI
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


@app.get("/nilai_csm")
def get_nilai_csm():
    return {
        "results": [
        {
            "Id_stakeholder": "001",
            "No_Registrasi_CSIRT": "083/CSIRT.01.10/BSSN/07/2022",
            "ID_Penilaian": "00001",
            "Nama_Stakeholder": "Lembaga AAAA",
            "Waktu Penilaian": "1/1/2024",
            "Tata Kelola": 3.80,
            "Identifikasi": 3.60,
            "Proteksi": 3.20,
            "Deteksi": 3.08,
            "Respon": 3.38,
            "Skor_Akhir": 3.41
        },
        {
            "Id_stakeholder": "002",
            "No_Registrasi_CSIRT": "123/CSIRT.01.10/BSSN/11/2022",
            "ID_Penilaian": "00002",
            "Nama_Stakeholder": "Lembaga BBBB",
            "Waktu Penilaian": "1/2/2024",
            "Tata Kelola": 3.51,
            "Identifikasi": 3.80,
            "Proteksi": 3.76,
            "Deteksi": 2.83,
            "Respon": 3.48,
            "Skor_Akhir": 3.48
        },
        {
            "Id_stakeholder": "003",
            "No_Registrasi_CSIRT": "156/CSIRT.01.05/BSSN/04/2023",
            "ID_Penilaian": "00003",
            "Nama_Stakeholder": "Lembaga CCCC",
            "Waktu Penilaian": "1/3/2024",
            "Tata Kelola": 3.69,
            "Identifikasi": 4.33,
            "Proteksi": 4.08,
            "Deteksi": 3.73,
            "Respon": 3.03,
            "Skor_Akhir": 3.77
        },
        {
            "Id_stakeholder": "004",
            "No_Registrasi_CSIRT": "236/CSIRT.0105/BSSN/08/2023",
            "ID_Penilaian": "00004",
            "Nama_Stakeholder": "Lembaga DDDD",
            "Waktu Penilaian": "1/4/2024",
            "Tata Kelola": 3.79,
            "Identifikasi": 3.74,
            "Proteksi": 4.22,
            "Deteksi": 3.63,
            "Respon": 3.88,
            "Skor_Akhir": 3.85
        },
        {
            "Id_stakeholder": "005",
            "No_Registrasi_CSIRT": "146/CSIRT.01.05/BSSN/02/2023",
            "ID_Penilaian": "00005",
            "Nama_Stakeholder": "Lembaga EEEE",
            "Waktu Penilaian": "1/5/2024",
            "Tata Kelola": 3.81,
            "Identifikasi": 4.28,
            "Proteksi": 4.17,
            "Deteksi": 3.95,
            "Respon": 3.44,
            "Skor_Akhir": 3.93
        },
        {
            "Id_stakeholder": "006",
            "No_Registrasi_CSIRT": "130/CSIRT.01.05/BSSN/12/2022",
            "ID_Penilaian": "00006",
            "Nama_Stakeholder": "Lembaga FFFF",
            "Waktu Penilaian": "1/6/2024",
            "Tata Kelola": 3.50,
            "Identifikasi": 4.08,
            "Proteksi": 4.09,
            "Deteksi": 4.10,
            "Respon": 4.01,
            "Skor_Akhir": 3.96
        },
        {
            "Id_stakeholder": "007",
            "No_Registrasi_CSIRT": "168/CSIRT.01.05/BSSN/05/2023",
            "ID_Penilaian": "00007",
            "Nama_Stakeholder": "Lembaga GGGG",
            "Waktu Penilaian": "1/7/2024",
            "Tata Kelola": 4.56,
            "Identifikasi": 4.35,
            "Proteksi": 4.69,
            "Deteksi": 3.94,
            "Respon": 4.20,
            "Skor_Akhir": 4.35
        },
        {
            "Id_stakeholder": "008",
            "No_Registrasi_CSIRT": "227/CSIRT.01.05/BSSN/08/2023",
            "ID_Penilaian": "00008",
            "Nama_Stakeholder": "Lembaga HHHH",
            "Waktu Penilaian": "1/8/2024",
            "Tata Kelola": 3.25,
            "Identifikasi": 4.07,
            "Proteksi": 3.65,
            "Deteksi": 3.15,
            "Respon": 2.91,
            "Skor_Akhir": 3.41
        }
    ]
}
