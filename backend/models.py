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

class PDFUploadStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    EXCEPTION = "Exception"

class UserPDFMappingData(BaseModel):
    pdfId: str
    pdfName: str
    pdfStatus: PDFUploadStatus

class UserPDFMappingSchema(BaseModel):
    userId: str
    createdAt: datetime
    pdfData: UserPDFMappingData

class PDFDataStatus(str, Enum):
    APPROVED = "approved".upper()
    REJECTED = "rejected".upper()

class PDFData(BaseModel):
    data: List[object]
    pdfDataStatus: PDFDataStatus