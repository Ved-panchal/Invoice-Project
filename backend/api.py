
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, ssl, cloudinary, cloudinary.uploader, json
from decouple import config
from pathlib import Path
from bson import ObjectId
from conversion import convert_image, convert_doc
from extraction import process_file
from rpc import RpcClient
from database_collections import MongoDBConnection
from fastapi import WebSocket, WebSocketDisconnect
from fastapi_socket import ConnectionManager

# # Mongo variables
# uri = config("MONGO_URI")
# db_name = config("MONGO_DB_NAME")
# user_collection_name = config("USER_COLLECTION_NAME")
# pdf_data_collection_name = config("PDF_DATA_COLLECTION_NAME")
# user_pdf_mapping_collection_name = config("USER_PDF_COLLECTION_NAME")

# mongo_client = pymongo.MongoClient(uri)
# db = mongo_client[db_name]
# users_collection = db[user_collection_name]
# pdf_data_collection = db[pdf_data_collection_name]
# user_pdf_mapping_collection = db[user_pdf_mapping_collection_name]

mongo_conn = MongoDBConnection()
# Access collections
users_collection = mongo_conn.get_users_collection()
pdf_data_collection = mongo_conn.get_pdf_data_collection()
user_pdf_mapping_collection = mongo_conn.get_user_pdf_mapping_collection()

manager = ConnectionManager()

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

@app.get("/hello")
def hello():
    return "hello"

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    # active_connections[user_id] = websocket

    try:
        while True:
            await websocket.receive_text()  # Keep the connection open and listen for incoming messages
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.post("/uploadFiles/{user_id}")
async def upload_files(user_id: str, background_tasks: BackgroundTasks, documents: list[UploadFile] = File(...)):
    response, filenames = [], []
    try:
        user_dir = STATIC_DIR / user_id
        if not user_dir.exists():
            os.makedirs(user_dir)

        # Insert initial data for all PDFs
        inserted_ids = []
        for document in documents:
            pdf_data = {
                "userId": int(user_id),
                "pdfData":{
                    "pdfId":"",
                    "pdfName":document.filename,
                    "pdfStatus":"Pending"
                }
            }
            result = user_pdf_mapping_collection.insert_one(pdf_data)
            pdf_data['_id'] = str(result.inserted_id) if result is not None else ""
            response.append(pdf_data)
            file_ext = document.filename.split('.')[-1].lower()
            new_file_name = f'{pdf_data["_id"]}.{file_ext}'
            filenames.append(new_file_name)
            file_location = user_dir / new_file_name

            with open(file_location, "wb") as f:
                f.write(document.file.read())


        # Schedule the upload_files_to_queue task as a background task
        background_tasks.add_task(upload_files_to_queue, filenames, user_id)


    except Exception as e:
        print("Error uploading files:", e)
        return {"success": False, "error": str(e)}
    return {"success": True, "result": response}

def upload_files_to_queue(filenames: list[str], user_id: str):
    try:
        # for filename in filenames:
        #     file_id = await store_pdf_data(user_id, filename)

        rpc_client = RpcClient()
        response = rpc_client.call({
            'user_id': user_id,
            'pdf_paths': filenames
        })
        print(f'user_id: {user_id}\nresponse from worker: {response}')

        print("message: ", "File uploaded successfully")
        # return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)})

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

@app.get('/get_pdfs/{user_id}')
def get_all_pdf_data_from_userid(user_id: int):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)
