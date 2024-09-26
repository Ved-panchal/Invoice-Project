from fastapi import File, HTTPException, UploadFile, BackgroundTasks, APIRouter, Depends
from starlette.responses import Response, JSONResponse


import os, json, requests
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from io import BytesIO

from models import PDFApprovalStatus, PDFUploadStatus
from util import utils, pdf_utils
from extraction import get_pdf_name, store_pdf_data
from database import mongo_conn
from queue_service import queue_manager
from routes import login_manager, STATIC_DIR
from together import Together
from decouple import config

api_router = APIRouter()

@api_router.post("/uploadFiles/{user_id}",tags=["v1"])
async def upload_files(user_id: str, response: Response, background_tasks: BackgroundTasks, documents: list[UploadFile] = File(...), user=Depends(login_manager)):
    filenames, uploaded_arr, not_uploaded_arr = [], [], []
    try:
        user_id = user['userId']
        user_dir = STATIC_DIR / user_id
        if not user_dir.exists():
            os.makedirs(user_dir)

        # Get total credits from db
        credits = mongo_conn.get_users_collection().find_one({"userId": user_id}, {"totalCredits": 1, "_id": 0})
        total_credits = credits['totalCredits']
        # print(f"total credits: {total_credits}")

        for document in documents:
            file_ext = document.filename.split('.')[-1].lower()

            file_data = document.file.read()
            buf = BytesIO(file_data)

            if file_ext == 'pdf':
                total_pages = pdf_utils.get_total_pages_pdf(buf)
            elif file_ext == 'docx':
                total_pages = pdf_utils.get_docx_page_count(buf)
            else:
                total_pages = 0
                raise Exception("Invalid file type.")

            # # get total pages for current document
            # print(f"total pages: {total_pages}")

            # check if total pages < total credits if yes then allow and subtract total credits by total pages else continue
            if total_pages <= total_credits:
                total_credits -= total_pages

                pdf_data = {
                    "userId": user_id,
                    "pdfData": {
                        "pdfId":"",
                        "pdfName": document.filename,
                        "pdfStatus": PDFUploadStatus.PENDING,
                        "pdfApprovalStatus": PDFApprovalStatus.PENDING,
                        "createdAt": datetime.now(),
                    }
                }

                result = mongo_conn.get_user_pdf_mapping_collection().insert_one(pdf_data)
                pdf_data['_id'] = str(result.inserted_id) if result is not None else ""
                pdf_data['pdfData']['id'] = pdf_data['_id']
                new_file_name = f'{pdf_data["_id"]}.{file_ext}'
                filenames.append(new_file_name)
                file_location = user_dir / new_file_name

                with open(file_location, "wb") as f:
                    f.write(file_data)

                uploaded_arr.append(document.filename)

            else:
                not_uploaded_arr.append(document.filename)

        response.status_code = 200
        response.body = json.dumps({"uploadedFiles": uploaded_arr, "notUploadedFiles": not_uploaded_arr}).encode()

        # Schedule the upload_files_to_queue task as a background task
        background_tasks.add_task(utils.upload_files_to_queue, queue_manager, filenames, user_id)

    except Exception as e:
        print("Error uploading files:", e)
        response.status_code = 500
        response.body = json.dumps({"error": str(e)}).encode()

    return response

@api_router.post('/delete_pdf',tags=["v1"])
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

@api_router.post('/invoice/get_data/{invoice_id}',tags=["v1"])
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

@api_router.post('/get_pdfs/{user_id}',tags=["v1"])
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

@api_router.get('/get_total_pages/{user_id}',tags=["v1"])
def get_total_pages(user_id: str, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        return mongo_conn.get_user_pdf_mapping_collection().count_documents({"userId": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post('/set_pdf_status',tags=["v1"])
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
                'pdfData.pdfApprovalStatus': PDFApprovalStatus.APPROVED if pdf_approval_status == "1" else PDFApprovalStatus.REJECTED
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

@api_router.get('/get_fields',tags=["v1"])
def get_fields(response: Response, user=Depends(login_manager)):
    try:
        user_id = user['userId']

        fields = mongo_conn.get_user_fields_collection().find_one({"userId": user_id}, {"fields": 1, "_id": 0})
        if fields is not None:
            fields = fields["fields"]
            response.status_code = 200
            response.body = json.dumps({"fields": fields}).encode()
        else:
            raise HTTPException(status_code=500, detail=f"Cannot find fields in database of user{user_id}")
        return response
    except Exception as e:
        response.status_code = 500
        raise HTTPException(status_code=500, detail=f"Unknown error has occured.\nDetails={str(e)}")

@api_router.post('/update_fields',tags=["v1"])
def update_fields(response: Response, payload: dict, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        fields = payload['fields']

        update_data = {
            '$set': {
                'fields': fields
            }
        }
        result = mongo_conn.get_user_fields_collection().update_one({"userId": user_id}, update_data)
        if result.modified_count == 1:
            response.status_code = 200
            response.body = json.dumps({"message": "Fields updated successfully."}).encode()
        else:
            response.status_code = 304
            response.body = json.dumps({"message": "Fields not modified."}).encode()
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"message": f"Unknown error has occured.\nDetails={str(e)}"}).encode()
        raise HTTPException(status_code=500, detail=f"Unknown error has occured.\nDetails={str(e)}")


def sap_login_call(sap_details):
    # print("making login request")
    response = requests.post(f"https://{sap_details['sapHost']}/b1s/v1/Login", json=sap_details['loginCredential'], verify=False)
    # print("login request status", response.status_code)
    data = json.loads(response.content.decode('utf-8'))
    # print("login request data", data)
    if response.status_code == 200:
        return data['SessionId']
    else:
        return None

def make_sap_call(sap_details, cardName):
    if(sap_details['sessionId'] == ''):
        sessionid = sap_login_call(sap_details)
        if sessionid:
            sap_details['sessionId'] = sessionid
            return make_sap_call(sap_details, cardName)
        return {"status": "failed login"}
    else:
        response = requests.get(f"https://{sap_details['sapHost']}/b1s/v1//Invoices?$select=CardCode&$filter=CardName eq '{cardName}'&$top=1",
                                cookies={"B1SESSION" : sap_details['sessionId']}, verify=False)
        if response.status_code == 401:
            sessionid = sap_login_call(sap_details)
            if sessionid:
                sap_details['sessionId'] = sessionid
                return make_sap_call(sap_details, cardName)
            return {"status": "failed login"}
        elif response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            # print('data by sap api', data)
            return {"status": "ok", "data": data, "sessionId": sap_details['sessionId']}
        else:
            # print('unknown error in sap : ', sap_details)
            return {"status": "failed"}


@api_router.post('/get_sap_data',tags=["v1"])
def get_sap_data(payload: dict, user=Depends(login_manager)):
    try:
        user_id = user['userId']
        # print("payload ->",payload)
        sap_details = mongo_conn.get_sap_detalis_collection().find_one({"userId" : user_id}, {"_id" : 0})
        # print("user id : ", user_id)
        if sap_details is not None:
            data = make_sap_call(sap_details, payload['cardName'])
            if data['sessionId'] != sap_details['sessionId']:
                update_data = {
                    '$set': {
                        'sessionId': data['sessionId']
                    }
                }
                mongo_conn.get_sap_detalis_collection().update_one({"userId" : user_id}, update_data)
            print("done making request data : ", data)
            if(data['data']['value'] == []):
                return {"status": "failed", "message": "check your card name"}
            return {"status": "ok", "CardCode" : data['data']['value'][0]['CardCode']}
        else :
            return {"status": "failed", "message":"Your Sap is not configured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unknown error has occured.\nDetails={str(e)}")
    

@api_router.post("/get_json_data",tags=["v1"])
async def upload_files_json(response: Response, documents: list[UploadFile] = File(...), user=Depends(login_manager)):
    filenames, uploaded_arr, not_uploaded_arr = [], [], []
    try:
        user_id = user['userId']
        user_dir = STATIC_DIR / user_id
        if not user_dir.exists():
            os.makedirs(user_dir)

        # Get total credits from db
        credits = mongo_conn.get_users_collection().find_one({"userId": user_id}, {"totalCredits": 1, "_id": 0})
        total_credits = credits['totalCredits']
        # print(f"total credits: {total_credits}")

        for document in documents:
            file_ext = document.filename.split('.')[-1].lower()

            file_data = document.file.read()
            buf = BytesIO(file_data)

            if file_ext == 'pdf':
                total_pages = pdf_utils.get_total_pages_pdf(buf)
            elif file_ext == 'docx':
                total_pages = pdf_utils.get_docx_page_count(buf)
            else:
                total_pages = 0
                raise Exception("Invalid file type.")

            # # get total pages for current document
            # print(f"total pages: {total_pages}")

            # check if total pages < total credits if yes then allow and subtract total credits by total pages else continue
            if total_pages <= total_credits:
                total_credits -= total_pages

                pdf_data = {
                    "userId": user_id,
                    "pdfData": {
                        "pdfId":"",
                        "pdfName": document.filename,
                        "pdfStatus": PDFUploadStatus.PENDING,
                        "pdfApprovalStatus": PDFApprovalStatus.PENDING,
                        "createdAt": datetime.now(),
                    }
                }

                result = mongo_conn.get_user_pdf_mapping_collection().insert_one(pdf_data)
                pdf_data['_id'] = str(result.inserted_id) if result is not None else ""
                pdf_data['pdfData']['id'] = pdf_data['_id']
                new_file_name = f'{pdf_data["_id"]}.{file_ext}'
                filenames.append(new_file_name)
                file_location = user_dir / new_file_name

                with open(file_location, "wb") as f:
                    f.write(file_data)

                uploaded_arr.append(document.filename)

            else:
                not_uploaded_arr.append(document.filename)


        # Schedule the upload_files_to_queue task as a background task

        client = Together(
            api_key=config(f"TOGETHER_API_KEY_4")
        )
        resultArr = []
        for Index ,file in enumerate(filenames):
            # print(file)
            result = store_pdf_data(client,user_id,file,STATIC_DIR)
            # print(result)
            if result is not None:
                response_json = {"FileName" : uploaded_arr[Index], "Data": result[2]}
            else:
                response_json = {"FileName" : uploaded_arr[Index], "Error": "Cant find result, Look into UI for status of pdf"}
            resultArr.append(response_json)
        response.status_code = 200
        response.body = json.dumps({"Uploaded Files" : resultArr}).encode()

    except Exception as e:
        print("Error uploading files:", e)
        response.status_code = 200
        response.body = json.dumps({"error": str(e)}).encode()

    return response