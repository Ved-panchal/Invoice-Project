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

class PDFApprovalStatus(str, Enum):
    PENDING = "pending".upper()
    APPROVED = "approved".upper()
    REJECTED = "rejected".upper()

class UserPDFMappingData(BaseModel):
    pdfId: str
    pdfName: str
    pdfStatus: PDFUploadStatus
    pdfApprovalStatus: PDFApprovalStatus
    createdAt: datetime

class UserPDFMappingSchema(BaseModel):
    userId: str
    pdfData: UserPDFMappingData

class PDFData(BaseModel):
    data: List[object]