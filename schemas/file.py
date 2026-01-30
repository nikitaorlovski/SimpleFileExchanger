from pydantic import BaseModel

class NewFile(BaseModel):
    filename: str
    content_type: str
    size: int
    path: str

    class Config:
        from_attributes = True