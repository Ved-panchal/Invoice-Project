
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os, ssl, cloudinary, cloudinary.uploader, json, asyncio
from datetime import datetime
from decouple import config
from pathlib import Path
from bson import ObjectId

from web_socket import socket_manager
from database import mongo_conn
from queue_service import queue_manager

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["http", "https"],
)

# Static file hosting
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/hello")
def hello():
    return "hello"

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await socket_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open and listen for incoming messages
    except WebSocketDisconnect:
        socket_manager.disconnect(user_id)

@app.post("/uploadFiles/{user_id}")
async def upload_files(user_id: str, background_tasks: BackgroundTasks, documents: list[UploadFile] = File(...)):
    response, filenames = [], []
    try:
        user_dir = STATIC_DIR / user_id
        if not user_dir.exists():
            os.makedirs(user_dir)

        for document in documents:
            pdf_data = {
                "userId": int(user_id),
                "createdAt": datetime.now(),
                "pdfData":{
                    "pdfId":"",
                    "pdfName":document.filename,
                    "pdfStatus":"Pending"
                }
            }
            result = mongo_conn.get_user_pdf_mapping_collection().insert_one(pdf_data)
            pdf_data['_id'] = str(result.inserted_id) if result is not None else ""
            pdf_data['pdfData']['id'] = pdf_data['_id']
            pdf_data['pdfData']['createdAt'] = pdf_data['createdAt']
            response.append(pdf_data['pdfData'])
            file_ext = document.filename.split('.')[-1].lower()
            new_file_name = f'{pdf_data["_id"]}.{file_ext}'
            filenames.append(new_file_name)
            file_location = user_dir / new_file_name

            with open(file_location, "wb") as f:
                f.write(document.file.read())

        # Schedule the upload_files_to_queue task as a background task
        background_tasks.add_task(upload_files_to_queue, filenames, user_id)
        # upload_files_to_queue(filenames, user_id)

    except Exception as e:
        print("Error uploading files:", e)
        return {"success": False, "error": str(e)}
    return {"success": True, "result": response}

def upload_files_to_queue(filenames: list[str], user_id: str):
    try:
        queue_manager.call(filenames, user_id)
        # await queue_manager.call(filenames, user_id)
        print("message: ", "File uploaded successfully")
        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)})

@app.post('/delete_pdf')
async def delete_file(payload: dict):
    mapping_obj_id = payload['fileId']
    try:
        data = mongo_conn.get_user_pdf_mapping_collection().find_one({"_id": ObjectId(mapping_obj_id)})
        if data is not None:
            user_id = data['userId']
            pdf_id = data['pdfData']['pdfId'][:-1]

            mongo_conn.get_user_pdf_mapping_collection().delete_one({"_id": ObjectId(mapping_obj_id)})
            if pdf_id:
                # delete from static folder here
                file_path: Path = STATIC_DIR / str(user_id) / (pdf_id + "0.pdf")
                if file_path.exists():
                    os.remove(file_path)
                mongo_conn.get_pdf_data_collection().delete_one({"_id": ObjectId(pdf_id)})
    except Exception as e:
        print(f'Error: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        data = mongo_conn.get_pdf_data_collection().find_one({"_id": ObjectId(invoice_id)})

        if data:
            data = convert_objectid(data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/get_pdfs/{user_id}')
def get_page_data_from_userid(user_id: int, payload: dict):
    try:
        page = payload['page'] or 1
        count = payload['count'] or 5
        response = []
        for record in mongo_conn.get_user_pdf_mapping_collection().find({"userId": user_id}).sort([("_id", -1)]).skip((page - 1) * count).limit(count):
            record["pdfData"]["id"] = convert_objectid(record["_id"])
            record["pdfData"]["createdAt"] = record["createdAt"]
            response.append(record)
        transformed_data = [item["pdfData"] for item in response]
        return transformed_data
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/get_total_pages/{user_id}')
def get_total_pages(user_id: int):
    try:
        return mongo_conn.get_user_pdf_mapping_collection().count_documents({"userId": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/insert_mapping_data')
def insert_mapping_data(payload: dict):
    try:
        inserted_id = mongo_conn.get_user_pdf_mapping_collection().insert_one(payload)
        if not inserted_id:
            print('Mapping data insertion error')
            raise HTTPException(status_code=400, detail="Mapping data insertion error")
        return inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_objectid(doc):
    try:
        if isinstance(doc, dict):
            return {key: convert_objectid(value) for key, value in doc.items()}
        elif isinstance(doc, list):
            return [convert_objectid(item) for item in doc]
        elif isinstance(doc, ObjectId):
            return str(doc)
        else:
            return doc
    except Exception as e:
        raise Exception(f'Error converting object_id\nDetails: {e}\nPlease contact administrator.')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)
