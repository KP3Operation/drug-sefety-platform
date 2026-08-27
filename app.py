from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(
    title="API Interaksi & Detail Obat",
    description="API untuk pengecekan interaksi obat"
)

# Menggunakan Master_DDI_Dataset.csv
CSV_FILE_PATH = "Master_DDI_Dataset.csv" 

try:
    df_interaksi = pd.read_csv(CSV_FILE_PATH)
    print("Dataset DDI berhasil dimuat!")
except Exception as e:
    df_interaksi = None
    print(f"Gagal memuat dataset: {e}")

class ObatRequest(BaseModel):
    obat_1: str
    obat_2: str

@app.get("/")
def home():
    return {
        "message": "API Interaksi Obat Aktif",
        "docs": "/docs",
        "dataset_loaded": df_interaksi is not None,
        "total_data": len(df_interaksi) if df_interaksi is not None else 0
    }

@app.post("/api/cek-interaksi")
async def cek_interaksi(data: ObatRequest):
    if df_interaksi is None:
        raise HTTPException(status_code=500, detail="Dataset belum dimuat di server.")
    
    try:
        o1 = data.obat_1.strip().lower()
        o2 = data.obat_2.strip().lower()
      
        hasil = df_interaksi[
            ((df_interaksi['Drug A'].str.lower() == o1) & (df_interaksi['Drug B'].str.lower() == o2)) |
            ((df_interaksi['Drug A'].str.lower() == o2) & (df_interaksi['Drug B'].str.lower() == o1))
        ]
        
        if hasil.empty:
            return {
                "status": "not_found",
                "message": f"Tidak ditemukan data interaksi antara {data.obat_1} dan {data.obat_2}."
            }

        row = hasil.iloc[0]
        return {
            "status": "success",
            "data": {
                "drug_1": row['Drug A'],
                "drug_2": row['Drug B'],
                "risk": row['Interaction description']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))