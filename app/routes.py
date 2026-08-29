from fastapi import APIRouter, HTTPException

from app import services
from app.schemas import ObatRequest

router = APIRouter()


@router.get("/api/health")
def health():
    return {
        "message": "API Interaksi Obat Aktif",
        "docs": "/docs",
        "model_loaded": services.model is not None
    }


@router.get("/api/obat")
def semua_obat():
    if services.df_info is None:
        raise HTTPException(status_code=500, detail="Dataset informasi obat belum dimuat di server.")

    return {
        "status": "success",
        "total_obat": len(services.df_info),
        "obat": (
            services.df_info[['drug_name', 'description']]
            .fillna("Data not available")
            .to_dict(orient="records")
        )
    }


@router.post("/api/cek-interaksi")
async def cek_interaksi(data: ObatRequest):
    if services.df_ddi is None:
        raise HTTPException(status_code=500, detail="Dataset belum dimuat di server.")

    try:
        return services.cek_interaksi(data.obat_1, data.obat_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
