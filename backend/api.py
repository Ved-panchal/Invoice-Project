from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os, json, ssl, cloudinary, cloudinary.uploader, pymongo
from decouple import config
from pathlib import Path
from bson import ObjectId
from conversion import convert_image, convert_doc
from extraction import get_invoice_data, get_invoice_data_text
from img_utils import process_image

# Mongo variables
uri = config("MONGO_URI")
db_name = config("MONGO_DB_NAME")
collection_name = config("COLLECTION_NAME")

mongo_client = pymongo.MongoClient(uri)
db = mongo_client[db_name]
handler = db[collection_name]

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Cloudinary configuration
cloudinary.config(
    cloud_name = config("CLOUDNARY_CLOUD_NAME"),
    api_key = config("CLOUDNARY_API_KEY"),
    api_secret = config("CLOUDNARY_SECRET")
)

# Static folder
STATIC_DIR = Path("static")

app = FastAPI()

# Allow cross origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file hosting
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load your OpenAI API key from environment variable
client = OpenAI(
    api_key = config('OPENAI_API_KEY')
)

@app.get("/hello")
def hello():
    """
    Simple API endpoint to test if the server is running.

    Returns:
    - str: A greeting message.
    """
    return "hello"

@app.post("/upload")
async def upload_file(document: UploadFile = File(...)):
    try:
        file_location = STATIC_DIR / document.filename
        with open(file_location, "wb") as f:
            f.write(document.file.read())

        file_ext = document.filename.split('.')[-1].lower()
        filename = document.filename
        if file_ext in ['doc', 'docx']:
            filename = await convert_doc(filename)

        elif file_ext in ['jpg', 'jpeg', 'png', 'tiff']:
            filename = await convert_image(filename)

        file_id = await process_file(filename)
        file_ext = filename.split('.')[-1]
        file_location = STATIC_DIR / filename

        # Construct new filename using file_id and the original extension
        new_filename = f"{file_id}.{file_ext}"
        new_file_location = STATIC_DIR / new_filename

        # Rename the file
        os.rename(file_location, new_file_location)

        return JSONResponse(content={"message": "File uploaded successfully", "file_id": file_id}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)}, status_code=500)

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
    
@app.get('/invoice/get_data/{invoice_id}')
def get_data_from_mongo(invoice_id: str):
    data = handler.find_one({"_id": ObjectId(invoice_id)})

    if data:
        data = convert_objectid(data)
    return data

def convert_objectid(doc):
    """
    Recursively converts ObjectId to string in the given document.
    """
    if isinstance(doc, dict):
        return {key: convert_objectid(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectid(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

async def process_file(filename: str) -> str:
    # await upload_file(file)
    # filename = payload.get("filename")
    file_ext = filename.split('.')[-1].lower()
    if file_ext == 'pdf':
        json_data =  await get_invoice_data_text(client, f"./static/{filename}")
        data = {'data' : json_data}
        result = handler.insert_one(data)
        if result:
            result = str(result.inserted_id) + "0"
        else:
            raise HTTPException(status_code=400, detail="Database insertion error")
        return result

    elif file_ext == "jpeg":
        if filename:
            (uploaded_image_urls, _) = await process_image(filename)
            json_data = await get_invoice_data(client, uploaded_image_urls)
            data = {'data' : [json_data]}
            result = handler.insert_one(data)
            if result:
                result = str(result.inserted_id) + "1"
            else:
                raise HTTPException(status_code=400, detail="Database insertion error")
            return result
        else:
            raise HTTPException(status_code=400, detail="Can not convert image to JPEG")
    else:
        raise HTTPException(status_code=400, detail='Unsupported file format')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)