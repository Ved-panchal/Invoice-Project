from enum import Enum
from pydantic import BaseModel
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