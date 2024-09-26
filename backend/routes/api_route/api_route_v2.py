from fastapi import File, HTTPException, UploadFile, APIRouter, Depends
from starlette.responses import Response, JSONResponse


import os, json, requests
from datetime import datetime
from io import BytesIO

from models import PDFApprovalStatus, PDFUploadStatus
from util import pdf_utils
from extraction import store_pdf_data
from database import mongo_conn
from routes import login_manager, STATIC_DIR
from together import Together
from decouple import config

api_router_v2 = APIRouter()
client = Together(
    api_key=config(f"TOGETHER_API_KEY_4")
)

@api_router_v2.post("/get_json_data",tags=["v2"])
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