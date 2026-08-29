import pickle
from pathlib import Path

from keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model_interaksi_obat.keras"
DATA_DIR = BASE_DIR / "data" / "processed"

model = None
drug_info_dict = None
df_info = None
df_ddi = None

try:
    model = load_model(MODEL_PATH)

    with open(DATA_DIR / "drug_info_dict.pkl", "rb") as f:
        drug_info_dict = pickle.load(f)

    with open(DATA_DIR / "df_info.pkl", "rb") as f:
        df_info = pickle.load(f)

    with open(DATA_DIR / "df_ddi.pkl", "rb") as f:
        df_ddi = pickle.load(f)

    print("Model dan semua komponen pickle berhasil dimuat")
except Exception as e:
    print(f"Gagal memuat model atau komponen: {e}")


def cek_interaksi(obat_1: str, obat_2: str) -> dict:
    o1 = obat_1.strip().lower()
    o2 = obat_2.strip().lower()

    hasil = df_ddi[
        ((df_ddi['Drug A'].str.lower() == o1) & (df_ddi['Drug B'].str.lower() == o2)) |
        ((df_ddi['Drug A'].str.lower() == o2) & (df_ddi['Drug B'].str.lower() == o1))
    ]

    if hasil.empty:
        interaction_desc = "No interaction description was found in the dataset."
        urgency_label = "⚪ - NO DATA / NOT YET VERIFIED."
        sumary_text = "Interaction data for this drug combination is not available."
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

    drug_info_lower = {k.lower(): v for k, v in drug_info_dict.items()}

    desc_a = drug_info_lower.get(o1, "Data not available")
    desc_b = drug_info_lower.get(o2, "Data not available")

    return {
        "status": "success",
        "clinical_report": {
            "drug_pair": f"{obat_1.upper()} + {obat_2.upper()}",
            "level_of_urgency": urgency_label,
            "quick_summary": sumary_text,
            "risk": interaction_desc,
            "medication_details": {
                obat_1.upper(): {"pharmacology_info": desc_a},
                obat_2.upper(): {"pharmacology_info": desc_b}
            }
        }
    }
