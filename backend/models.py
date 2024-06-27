from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import List

# Enum for data type
class DataType(Enum):
    IMAGEURL = "imageurl",
    TEXT = "text"

class ImageUrls(BaseModel):
    imageUrl: List[str]

class TextData(BaseModel):
    pdf_path: str

class User(BaseModel):
    username: str
    password: str

class PDFData(BaseModel):
    pdfId: str
    pdfName: str
    pdfStatus: str

class PDFSchema(BaseModel):
    userId: str
    createdAt: datetime
    pdfData: PDFData