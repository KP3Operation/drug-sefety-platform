from pydantic import BaseModel


class ObatRequest(BaseModel):
    obat_1: str
    obat_2: str
