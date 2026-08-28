from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import pickle
import tensorflow as tf
from keras.models import load_model

app = FastAPI(
    title="API Interaksi & Detail Obat",
    description="API untuk pengecekan interaksi obat"
)

try:
    model = load_model('model_interaksi_obat.keras')

    with open('drug_info_dict.pkl', 'rb') as f:
        drug_info_dict = pickle.load(f)
    
    with open('df_info.pkl', 'rb') as f:
        df_info = pickle.load(f)
        
    with open('df_ddi.pkl', 'rb') as f:
        df_ddi = pickle.load(f)
        
    print("Model dan semua komponen pickle berhasil dimuat")
except Exception as e:
    print(f"Gagal memuat model atau komponen: {e}")

class ObatRequest(BaseModel):
    obat_1: str
    obat_2: str

@app.get("/")
def home():
    return {
        "message": "API Interaksi Obat Aktif",
        "docs": "/docs",
        "model_loaded": 'model' in globals()
    }

@app.post("/api/cek-interaksi")
async def cek_interaksi(data: ObatRequest):
    if 'df_ddi' not in globals() or df_ddi is None:
        raise HTTPException(status_code=500, detail="Dataset belum dimuat di server.")
    
    try:
        o1 = data.obat_1.strip().lower()
        o2 = data.obat_2.strip().lower()
      
        hasil = df_ddi[
            ((df_ddi['Drug A'].str.lower() == o1) & (df_ddi['Drug B'].str.lower() == o2)) |
            ((df_ddi['Drug A'].str.lower() == o2) & (df_ddi['Drug B'].str.lower() == o1))
        ]
        
        if hasil.empty:
            interaction_desc = "Deskripsi interaksi tidak ditemukan dalam dataset."
            urgency_label = "⚪ - TIDAK ADA DATA / BELUM TERVERIFIKASI."
            sumary_text = "Data interaksi untuk kombinasi obat ini tidak tersedia."
        else:
            row = hasil.iloc[0]
            interaction_desc = row['Interaction description']
            desc_lower = interaction_desc.lower()

            if any(keyword in desc_lower for keyword in ["heart failure", "hypotension", "increased", "severity", "risk", "cogestive"]):
                urgency_label = "🔴 - HIGH (CONTRAINDICATION)."
                sumary_text = "Dangerous interaction! Significant clinical risk to the patient."
            else:
                urgency_label = "🟡 - MODERATE (CAUTION)."
                sumary_text = "Moderate interaction. Monitor patient closely."

        obat_1_lower = data.obat_1.strip().lower()
        obat_2_lower = data.obat_2.strip().lower()

        drug_info_lower = {k.lower(): v for k, v in drug_info_dict.items()}

        desc_a = drug_info_lower.get(obat_1_lower, "Data not available")
        desc_b = drug_info_lower.get(obat_2_lower, "Data not available")
            
        return {
            "status": "success",
            "clinical_report": {
                "drug_pair": f"{data.obat_1.upper()} + {data.obat_2.upper()}",
                "level_of_urgency": urgency_label,
                "quick_summary": sumary_text,
                "risk": interaction_desc,
                "medication_details": {
                    data.obat_1.upper(): {"utility": desc_a},
                    data.obat_2.upper(): {"utility": desc_b}
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))