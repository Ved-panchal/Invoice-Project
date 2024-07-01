from fastapi import File, HTTPException, UploadFile, BackgroundTasks, APIRouter, Depends
from starlette.responses import Response

import os, json
from datetime import datetime
from pathlib import Path
from bson import ObjectId

from models import PDFDataStatus, PDFUploadStatus
from util import utils, pdf_utils
from extraction import get_pdf_name
from database import mongo_conn
from queue_service import queue_manager
from routes import login_manager, STATIC_DIR

api_router = APIRouter()

@api_router.post("/uploadFiles/{user_id}")
async def upload_files(user_id: str, background_tasks: BackgroundTasks, documents: list[UploadFile] = File(...), user=Depends(login_manager)):
    response, filenames = [], []
    try:
        user_id = user['userId']
        user_dir = STATIC_DIR / user_id
        if not user_dir.exists():
            os.makedirs(user_dir)

        for document in documents:
            pdf_data = {
                "userId": user_id,
                "pdfData": {
                    "pdfId":"",
                    "pdfName": document.filename,
                    "pdfStatus": PDFUploadStatus.PENDING,
                    "pdfApprovalStatus": PDFDataStatus.PENDING,
                    "createdAt": datetime.now(),
                }
            }
            # print(pdf_data)
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
async def delete_file(payload: dict, response: Response, user=Depends(login_manager)):
    mapping_obj_id = payload['fileId']
    try:
        data = mongo_conn.get_user_pdf_mapping_collection().find_one({"_id": ObjectId(mapping_obj_id)})
        if data is not None:
            user_id = data['userId']
            # If user id received from database and user id in session is not same, throw error
            if user_id != user['userId']:
                raise HTTPException(status_code=401, detail="Invalid login, please login with valid credentials.")

            pdf_id = data['pdfData']['pdfId'][:-1]

            mongo_conn.get_user_pdf_mapping_collection().delete_one({"_id": ObjectId(mapping_obj_id)})
            if pdf_id:
                # delete from static folder here
                file_path: Path = STATIC_DIR / str(user_id) / (pdf_id + "0.pdf")
                if file_path.exists():
                    os.remove(file_path)
                mongo_conn.get_pdf_data_collection().delete_one({"_id": ObjectId(pdf_id)})
            response.status_code = 200
            response.body = json.dumps({"message": "File deleted successfully"}).encode()
            return response
    except Exception as e:
        print(f'Error: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post('/invoice/get_data/{invoice_id}')
def get_data_from_mongo(invoice_id: str, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        data = mongo_conn.get_pdf_data_collection().find_one({"_id": ObjectId(invoice_id)})
        pdf_name = get_pdf_name(user_id, invoice_id + "0")
        if data:
            data = utils.convert_objectid(data)
            data['pdfName'] = pdf_name

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post('/get_pdfs/{user_id}')
def get_page_data_from_userid(user_id: str, payload: dict, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        page = payload['page'] or 1
        count = payload['count'] or 5
        response = []
        for record in mongo_conn.get_user_pdf_mapping_collection().find({"userId": user_id}).sort([("_id", -1)]).skip((page - 1) * count).limit(count):
            record["pdfData"]["id"] = utils.convert_objectid(record["_id"])
            # record["pdfData"]["createdAt"] = record["createdAt"]
            response.append(record)
        transformed_data = [item["pdfData"] for item in response]
        return transformed_data
    except Exception as e:
        print(f'Error in get_pdfs: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get('/get_total_pages/{user_id}')
def get_total_pages(user_id: str, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        return mongo_conn.get_user_pdf_mapping_collection().count_documents({"userId": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post('/set_pdf_status')
def set_pdf_status(payload: dict, response: Response, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        invoice_id = payload['invoiceId']
        updated_data = payload['updatedData']
        pdf_approval_status = payload['pdfApprovalStatus']
        # invoice_id without 0 and .pdf added
        pdf_path = STATIC_DIR / user_id / (invoice_id + "0.pdf")
        update_operation_pdf_data = {
            '$set': {
                'data': pdf_utils.get_cords_of_word(updated_data, pdf_path),
                # 'pdfApprovalStatus': PDFDataStatus.APPROVED if pdf_status == "1" else PDFDataStatus.REJECTED
            }
        }
        update_operation_pdf_mapping_data = {
            '$set': {
                'pdfData.pdfApprovalStatus': PDFDataStatus.APPROVED if pdf_approval_status == "1" else PDFDataStatus.REJECTED
            }
        }
        result_pdf_data = mongo_conn.get_pdf_data_collection().update_one({"_id": ObjectId(invoice_id)}, update_operation_pdf_data)
        result_pdf_mapping_data = mongo_conn.get_user_pdf_mapping_collection().update_one({ "pdfData.pdfId": (invoice_id + "0") }, update_operation_pdf_mapping_data)
        if result_pdf_data.modified_count == 1 and result_pdf_mapping_data.modified_count == 1:
            response.status_code = 200
            response.body = json.dumps({"message": "PDF data approved."}).encode()
        elif result_pdf_data.matched_count == 1 and result_pdf_data.modified_count == 0:
            response.status_code = 200
            response.body = json.dumps({f"message": "PDF data is already approved or rejected."}).encode()
        elif result_pdf_data.matched_count == 0:
            response.status_code = 400
            response.body = json.dumps({f"message": "PDF is not found."}).encode()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unknown error has occured.\nDetails={str(e)}")