# from xml.dom.minidom import Document
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
import cv2, ssl, pymupdf
import numpy as np
import cloudinary
import cloudinary.uploader
from PIL import Image
import requests
from io import BytesIO
import pytesseract
from typing import List
from docx2pdf import convert
import win32com.client

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Cloudinary configuration
cloudinary.config(
    cloud_name='dcea4t8q2',
    api_key='448278165688468',
    api_secret='j8Eeylq1vfAcwhp8nCVoALCht3c'
)

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


#ankur code


def upload_image_to_cloudinary(image_np, filename, page_number):
    _, img_encoded = cv2.imencode('.jpg', image_np)
    img_io = BytesIO(img_encoded)
    img_io.name = f'image{page_number+1}.jpg'
    
    upload_result = cloudinary.uploader.upload(
        img_io, 
        folder='output_images', 
        public_id=f'{filename}/image{page_number+1}'
    )
    return upload_result['url']

def process_pdf(pdf_path, output_folder, filename):
    pdf_document = pymupdf.open(pdf_path)
    uploaded_image_urls = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        # Set the zoom level
        mat = pymupdf.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to a numpy array
        image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        if image_np.shape[2] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)

        uploaded_image_urls.append(upload_image_to_cloudinary(image_np, filename, page_number))

    pdf_document.close()
    return uploaded_image_urls

async def process_image(file, filename):
    # image_bytes = await file.read()
    try:
        image = Image.open(f"input/{filename}")
    except Exception as e:
        return [], f"Error opening image: {e}"
    
    if not image:
        return [], "Failed to open image"
    image_np = np.array(image.convert('L'))
    
    text = pytesseract.image_to_string(image_np)
    
    uploaded_image_urls = [upload_image_to_cloudinary(image_np, filename, 0)]
    
    return uploaded_image_urls,text


def convert_doc(file,input_folder,output_folder):
    input_path = os.path.join(input_folder, file.filename)
    output_filename = f"{os.path.splitext(file.filename)[0]}.pdf"
    output_path = os.path.join(output_folder, output_filename)

    # Save the uploaded file to the input folder
    file.save(input_path)

    # Convert the file to PDF
    convert(input_path, output_path)
    
    return output_path


# def docx_to_pdf(docx_path, pdf_path):
#     doc = Document(docx_path)
#     doc.save(pdf_path)

# def doc_to_pdf(doc_path, pdf_path):
#     word = win32com.client.Dispatch("Word.Application")
#     word.Visible = False
#     doc = word.Documents.Open(doc_path)
#     doc.SaveAs(pdf_path, FileFormat=17)
#     doc.Close()
#     word.Quit()

# def convert_to_pdf_and_return_path(input_path, output_folder):
#     output_filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
#     output_path = os.path.join(output_folder, output_filename)

#     if input_path.endswith(".docx"):
#         docx_to_pdf(input_path, output_path)
#     elif input_path.endswith(".doc"):
#         doc_to_pdf(input_path, output_path)
#     else:
#         return json.dumps({"error": "Unsupported file format"})

#     return json.dumps({"output_path": output_path})


@app.post('/process_file')
async def process_file(file: UploadFile = File(...)):
    filename = file.filename
    input_folder = "input"
    input_file_path = os.path.join(input_folder, filename)
    with open(input_file_path, "wb") as buffer:
        buffer.write(await file.read())

    output_folder = "output"
    file_ext = filename.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        print("pdf")
        # text=[]
        # uploaded_image_urls = process_pdf(input_file_path, output_folder, filename)
        # for url in uploaded_image_urls:
        #     text.append(extract_text_from_image_url(url))
        # return jsonify({'text': text})
        # return jsonify({'urls': uploaded_image_urls})
    elif file_ext in ['doc', 'docx']:
        path=convert_doc(file,input_folder,output_folder)
        return {'output_odf_path': path}
        # extract text API
    elif file_ext in ['jpg', 'jpeg', 'png','tif']:
        text=[]
        uploaded_image_urls,text = await process_image(file, filename)
        
        return {'text': text,'urls':uploaded_image_urls}   
    else:
        raise HTTPException(status_code=400, detail='Unsupported file format')

@app.post('/delete_folder')
async def delete_folder(folder_name: str):
    if not folder_name:
        raise HTTPException(status_code=400, detail='No folder name provided')

    try:
        # Delete all resources inside the folder
        cloudinary.api.delete_resources_by_prefix(f'output_images/{folder_name}')
        
        # Delete the folder itself
        cloudinary.api.delete_folder(f'output_images/{folder_name}')

        return {'message': f'Folder {folder_name} and its contents have been deleted successfully.'}
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)