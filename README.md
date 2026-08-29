# Drug Safety Platform

Platform pengecekan keamanan interaksi obat (drug-drug interaction). Backend FastAPI melakukan
lookup interaksi antar obat berdasarkan dataset DDI (Drug-Drug Interaction) yang berisi 1964 obat,
dan menyediakan halaman testing sederhana untuk mencoba endpoint-nya secara langsung dari browser.

## Struktur Folder

```
drug-sefety-platform/
├── app/                # Backend FastAPI
│   ├── main.py         # Instance FastAPI, mount frontend, include routes
│   ├── schemas.py       # Pydantic request models
│   ├── routes.py        # Endpoint API (/api/health, /api/obat, /api/cek-interaksi)
│   └── services.py      # Loading model/dataset & logic pengecekan interaksi
├── data/
│   ├── raw/              # Dataset CSV mentah (sumber training)
│   └── processed/        # Hasil olahan (.pkl) yang dipakai backend saat runtime
├── models/
│   └── model_interaksi_obat.keras
├── frontend/
│   └── index.html        # Halaman testing 1 file (Tailwind CDN + vanilla JS)
├── reference/
│   └── Fitur_Kombinasi_Obat.ipynb   # Notebook riset & training model
├── requirements.txt
└── .gitignore
```

## Setup & Instalasi

TensorFlow belum menyediakan wheel untuk Python 3.14, jadi gunakan **Python 3.11** untuk virtual
environment proyek ini.

```
py -3.11 -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
```

## Menjalankan Aplikasi

```
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- Halaman testing frontend: http://127.0.0.1:8000/
- Swagger UI (dokumentasi interaktif): http://127.0.0.1:8000/docs

## Dokumentasi API

### `GET /api/health`
Mengecek status API dan apakah model/dataset berhasil dimuat.

```json
{
  "message": "API Interaksi Obat Aktif",
  "docs": "/docs",
  "model_loaded": true
}
```

### `GET /api/obat`
Mengembalikan seluruh daftar obat beserta deskripsinya.

```json
{
  "status": "success",
  "total_obat": 1964,
  "obat": [
    { "drug_name": "Fenofibrate", "description": "Fenofibrate is a fibric acid derivative..." }
  ]
}
```

### `POST /api/cek-interaksi`
Mengecek interaksi antara dua obat.

Request:
```json
{ "obat_1": "Nifedipine", "obat_2": "Esmolol" }
```

Response:
```json
{
  "status": "success",
  "clinical_report": {
    "drug_pair": "NIFEDIPINE + ESMOLOL",
    "level_of_urgency": "🔴 - HIGH (CONTRAINDICATION).",
    "quick_summary": "Dangerous interaction! Significant clinical risk to the patient.",
    "risk": "The risk or severity of congestive heart failure and hypotension can be increased when Nifedipine is combined with Esmolol.",
    "medication_details": {
      "NIFEDIPINE": { "pharmacology_info": "..." },
      "ESMOLOL": { "pharmacology_info": "..." }
    }
  }
}
```

## Known Limitations

- Model `.keras` yang di-load saat ini adalah model placeholder yang **belum pernah dilatih**
  (dibuat di cell terakhir `reference/Fitur_Kombinasi_Obat.ipynb`), menimpa model BiLSTM asli
  yang sebenarnya sudah dilatih dengan akurasi validasi 99.97% pada notebook yang sama.
- Logic `/api/cek-interaksi` saat ini **tidak memanggil model** sama sekali — hasil sepenuhnya
  berasal dari lookup langsung ke tabel `df_ddi` berdasarkan exact match nama obat, ditambah
  pencocokan kata kunci pada teks deskripsi interaksi untuk menentukan level urgency.
- Ini berarti pasangan obat yang namanya tidak persis cocok dengan dataset, atau yang belum
  memiliki baris interaksi di `df_ddi`, akan selalu dikembalikan sebagai "NO DATA" walau
  secara klinis mungkin berinteraksi.

Perbaikan yang disarankan untuk iterasi berikutnya: retrain & simpan ulang model BiLSTM yang
benar, lalu integrasikan hasil inferensinya ke `app/services.py` sebagai pelengkap (atau
pengganti) logic lookup saat ini.
