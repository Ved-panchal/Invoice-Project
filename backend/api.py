import asyncio
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os, json, ssl, cloudinary, cloudinary.uploader, pymongo
from decouple import config
from pathlib import Path
from bson import ObjectId
from together import Together
from conversion import convert_image, convert_doc
from extraction import get_invoice_data, get_invoice_data_text
from img_utils import process_image

# Mongo variables
uri = config("MONGO_URI")
db_name = config("MONGO_DB_NAME")
user_collection_name = config("USER_COLLECTION_NAME")
pdf_data_collection_name = config("PDF_DATA_COLLECTION_NAME")
user_pdf_mapping_collection_name = config("USER_PDF_COLLECTION_NAME")

mongo_client = pymongo.MongoClient(uri)
db = mongo_client[db_name]
users_collection = db[user_collection_name]
pdf_data_collection = db[pdf_data_collection_name]
user_pdf_mapping_collection = db[user_pdf_mapping_collection_name]

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Cloudinary configuration
cloudinary.config(
    cloud_name=config("CLOUDNARY_CLOUD_NAME"),
    api_key=config("CLOUDNARY_API_KEY"),
    api_secret=config("CLOUDNARY_SECRET")
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

# Together API client
client = Together(api_key=config("TOGETHER_API_KEY"))
# client = OpenAI(
#     api_key = config(f'OPENAI_API_KEY')
# )

# Active WebSocket connections
active_connections = {}

@app.get("/hello")
def hello():
    return "hello"

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open and listen for incoming messages
    except WebSocketDisconnect:
        del active_connections[user_id]

async def watch_mongo_changes():
    change_stream = user_pdf_mapping_collection.watch(full_document="updateLookup")

    async for change in change_stream:
        full_document = change["fullDocument"]
        user_id = full_document.get("userId")
        if user_id in active_connections:
            message = json.dumps(full_document)
            await active_connections[user_id].send_text(message)

# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(watch_mongo_changes())

@app.post("/uploadFiles/{user_id}")
async def upload_files(user_id: int, documents: list[UploadFile] = File(...)):
    response = []
    try:
        user_dir = STATIC_DIR / str(user_id)
        if not user_dir.exists():
            os.makedirs(user_dir)

        # Insert initial data for all PDFs
        inserted_ids = []
        for document in documents:
            result = user_pdf_mapping_collection.insert_one({
                "userId": user_id,
                "pdfData": {
                    "pdfId": "",
                    "pdfName": document.filename,
                    "pdfStatus": "Pending"
                }
            })
            inserted_ids.append(result.inserted_id)
            response.append(str(result.inserted_id)) if result else response.append("")

        # Process each file and update the corresponding document
        for document, inserted_id in zip(documents, inserted_ids):
            file_location = user_dir / document.filename
            with open(file_location, "wb") as f:
                f.write(document.file.read())
                
            filename = document.filename
            file_id = await process_file(filename, user_id)
            file_ext = filename.split('.')[-1]
            file_location = STATIC_DIR / str(user_id) / filename

            new_filename = f"{file_id}.{file_ext}"
            new_file_location = STATIC_DIR / str(user_id) / new_filename
            os.rename(file_location, new_file_location)

            user_pdf_mapping_collection.update_one(
                {"_id": inserted_id},
                {"$set": {"pdfData.pdfId": file_id, "pdfData.pdfStatus": "Completed"}}
            )

            # Send the update to the WebSocket connection
            if user_id in active_connections:
                await active_connections[user_id].send_text(json.dumps({
                    "pdfId": file_id,
                    "pdfName": document.filename,
                    "pdfStatus": "Completed"
                }))

    except Exception as e:
        print("Error uploading files:", e)
        return {"success": False, "error": str(e)}
    return {"success": True, "result": response}

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

        new_filename = f"{file_id}.{file_ext}"
        new_file_location = STATIC_DIR / new_filename

        os.rename(file_location, new_file_location)

        return JSONResponse(content={"message": "File uploaded successfully", "file_id": file_id}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)}, status_code=500)

@app.post('/delete_folder')
async def delete_folder(folder_name: str):
    if not folder_name:
        raise HTTPException(status_code=400, detail='No folder name provided')

    try:
        cloudinary.api.delete_resources_by_prefix(f'output_images/{folder_name}')
        cloudinary.api.delete_folder(f'output_images/{folder_name}')

        return {'message': f'Folder {folder_name} and its contents have been deleted successfully.'}
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/invoice/get_data/{invoice_id}')
def get_data_from_mongo(invoice_id: str):
    data = pdf_data_collection.find_one({"_id": ObjectId(invoice_id)})

    if data:
        data = convert_objectid(data)
    return data

@app.post('/get_pdfs')
def get_all_pdf_data_from_userid(payload: dict):
    user_id = int(payload.get("userId"))
    response = []
    for record in user_pdf_mapping_collection.find({"userId": user_id}, {"_id": 0, "userId": 0}).sort([("_id", -1)]).limit(5):
        response.append(record)
    transformed_data = [item["pdfData"] for item in response]
    return transformed_data

@app.post('/insert_mapping_data')
def insert_mapping_data(payload: dict):
    try:
        inserted_id = user_pdf_mapping_collection.insert_one(payload)
        if not inserted_id:
            print('Mapping data insertion error')
            raise HTTPException(status_code=400, detail="Mapping data insertion error")
        return inserted_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def convert_objectid(doc):
    if isinstance(doc, dict):
        return {key: convert_objectid(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectid(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

async def process_file(filename: str, user_id: int) -> str:
    file_ext = filename.split('.')[-1].lower()
    if file_ext == 'pdf':
        json_data = await get_invoice_data_text(client, f"./static/{str(user_id)}/{filename}")
        data = {'data': json_data}
        result = pdf_data_collection.insert_one(data)
        if result:
            result = str(result.inserted_id) + "0"
        else:
            raise HTTPException(status_code=400, detail="Database insertion error")
        return result

    elif file_ext == "jpeg":
        if filename:
            (uploaded_image_urls, _) = await process_image(filename)
            json_data = await get_invoice_data(client, uploaded_image_urls)
            data = {'data': [json_data]}
            result = pdf_data_collection.insert_one(data)
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
