from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import os, json
from enum import Enum
from decouple import config
from pdf_utils import get_cords_of_word, extract_invoice_data_pdf
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path


STATIC_DIR = Path("static")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

class DataType(Enum):
    IMAGEURL = "imageurl",
    TEXT = "text"

class ImageUrls(BaseModel):
    imageUrl: List[str]

class TextData(BaseModel):
    pdf_path: str

# Load your OpenAI API key from environment variable
client = OpenAI(
    # This is the default and can be omitted
    # api_key=os.environ.get("OPENAI_API_KEY"),
    api_key = config('OPENAI_API_KEY')
)

def prepare_prompt(text=""):
    """
    Prepare the prompt for the OpenAI API to extract invoice data.

    Args:
    - text (str): The text extracted from the PDF.

    Returns:
    - str: The prepared prompt with the given text and instructions for data extraction.
    """
    invoiceData = {
        "CardCode": "V10000",
        "TaxDate": "2024-05-20",
        "DocDate": "2024-05-21",
        "DocDueDate": "2024-06-25",
        "CardName": "Acme Associates",
        "DiscountPercent": "10.00",
        "DocumentLines": [
            {
                "ItemCode": "A00001",
                "Quantity": "100",
                "TaxCode": "TAXON",
                "UnitPrice": "50"
            }
        ]
    }
    prompt = (
        f"{text}\n"
        "Extract the following data from this invoice text:\n\n"
        "1. CardCode (vendor id)\n"
        "2. TaxDate (keep date format as it is in pdf)\n"
        "3. DocDate (keep date format as it is in pdf)\n"
        "4. DocDueDate (keep date format as it is in pdf)\n"
        "5. CardName (vendor name)\n"
        "6. DiscountPercent\n"
        "7. DocumentLines (array of line items)\n"
        "   - ItemCode\n"
        "   - Quantity\n"
        "   - TaxCode\n"
        "   - UnitPrice\n\n"
        "Return the data in the following JSON format, and ensure the data is accurate and formatted correctly.\n"
        f"{invoiceData}\n"
        "Give me strictly in JSON format, don't include any unnecessary headings, newline characters, or \\ before inverted commas."
    )

    return prompt

def extract_invoice_data(data_type: DataType, text):
    """
    Extract invoice data using OpenAI API based on the data type.

    Args:
    - data_type (DataType): The type of data (IMAGEURL or TEXT).
    - text (Union[str, List[str]]): The text extracted from PDF or list of image URLs.

    Returns:
    - str: The extracted invoice data in JSON format.
    """
    if data_type == DataType.IMAGEURL:
        prompt = prepare_prompt()
        messages = [{"role": "user", "content": [prompt]}]
        for url in text:
            messages[0]["content"].append({"type": "image_url", "image_url": {"url": url}})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0
        )
    else:
        prompt = prepare_prompt(text)
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )

    return response.choices[0].message.content


@app.post("/upload/")
async def upload_file(document: UploadFile = File(...)):
    try:
        file_location = STATIC_DIR / document.filename
        with open(file_location, "wb") as f:
            f.write(document.file.read())
        return JSONResponse(content={"message": "File uploaded successfully", "filename": document.filename}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)}, status_code=500)


@app.post("/getInvoiceData/image")
async def get_invoice_data(image_urls: ImageUrls) -> dict:
    """
    API endpoint to extract invoice data from image URLs.

    Args:
    - image_urls (ImageUrls): A list of image URLs containing invoice images.

    Returns:
    - dict: The extracted invoice data in JSON format.

    Raises:
    - HTTPException: If no image URLs are provided or an error occurs during processing.
    """
    if not image_urls.imageUrl:
        raise HTTPException(status_code=400, detail="No image URLs provided")

    try:
        result = extract_invoice_data(DataType.IMAGEURL, image_urls.imageUrl)
        json_response = json.loads(result)
        return json_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/getInvoiceData/text")
async def get_invoice_data_text(data: TextData) -> list:
    """
    API endpoint to extract invoice data from text extracted from a PDF.

    Args:
    - data (TextData): The path to the PDF file.

    Returns:
    - list: A list containing the extracted invoice data in JSON format and the coordinates of the extracted words.

    Raises:
    - HTTPException: If no text is provided or an error occurs during processing.
    """
    pdf_path = data.pdf_path
    if not pdf_path:
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        pdf_data = extract_invoice_data_pdf(pdf_path)
        result = extract_invoice_data(DataType.TEXT, pdf_data)
        json_data = json.loads(result)
        res_list = get_cords_of_word(json_data, pdf_path)
        res_list.insert(0, json_data)
        return res_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.route("/hello", methods=["GET"])
def hello():
    """
    Simple API endpoint to test if the server is running.

    Returns:
    - str: A greeting message.
    """
    return "hello"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)

