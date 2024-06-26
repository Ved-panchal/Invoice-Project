from fastapi import File, HTTPException, UploadFile, BackgroundTasks, APIRouter, Depends

import os
from datetime import datetime
from pathlib import Path
from bson import ObjectId

from util import utils
from database import mongo_conn
from queue_service import queue_manager
from routes import login_manager, STATIC_DIR

api_router = APIRouter()

@api_router.post("/uploadFiles/{user_id}")
async def upload_files(user_id: str, background_tasks: BackgroundTasks, documents: list[UploadFile] = File(...), user=Depends(login_manager)):
    response, filenames = [], []
    try:
        user_id1 = user['username']
        print(user_id1)
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
        background_tasks.add_task(utils.upload_files_to_queue, queue_manager, filenames, user_id)
        # upload_files_to_queue(filenames, user_id)

    except Exception as e:
        print("Error uploading files:", e)
        return {"success": False, "error": str(e)}
    return {"success": True, "result": response}

@api_router.post('/delete_pdf')
async def delete_file(payload: dict, user=Depends(login_manager)):
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

@api_router.get('/invoice/get_data/{invoice_id}')
def get_data_from_mongo(invoice_id: str):
    try:
        data = mongo_conn.get_pdf_data_collection().find_one({"_id": ObjectId(invoice_id)})

        if data:
            data = utils.convert_objectid(data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post('/get_pdfs/{user_id}')
def get_page_data_from_userid(user_id: int, payload: dict, user=Depends(login_manager)):
    try:
        page = payload['page'] or 1
        count = payload['count'] or 5
        response = []
        for record in mongo_conn.get_user_pdf_mapping_collection().find({"userId": user_id}).sort([("_id", -1)]).skip((page - 1) * count).limit(count):
            record["pdfData"]["id"] = utils.convert_objectid(record["_id"])
            record["pdfData"]["createdAt"] = record["createdAt"]
            response.append(record)
        transformed_data = [item["pdfData"] for item in response]
        return transformed_data
    except Exception as e:
        print(f'Error in get_pdfs: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get('/get_total_pages/{user_id}')
def get_total_pages(user_id: int, user=Depends(login_manager)):
    try:
        return mongo_conn.get_user_pdf_mapping_collection().count_documents({"userId": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
