from fastapi import File, HTTPException, UploadFile, APIRouter, Depends
from starlette.responses import Response, JSONResponse
from pydantic import BaseModel


import os, json, requests
from datetime import datetime
from io import BytesIO
from pymongo.collection import ReturnDocument

from models import PDFApprovalStatus, PDFUploadStatus
from util import pdf_utils
from extraction.extract_v2 import _store_pdf_data as store_pdf_data_v2
from database import mongo_conn
from routes import login_manager_v2, STATIC_DIR
from together import Together
from decouple import config
from routes.dependencies import role_required
from extraction.prompt import _default_fields

from doctr.models import ocr_predictor


api_router_v2 = APIRouter()
client = Together(
    api_key=config(f"TOGETHER_API_KEY_4")
)
ocrmodel = ocr_predictor('db_resnet50', 'crnn_vgg16_bn', pretrained=True)


@api_router_v2.get("/hello")
def hello(user=Depends(login_manager_v2)):
    # print(f"username: {user.username}")
    print(f"user: {user}")
    print(f"username: {user['username']}")
    return "hello"

@api_router_v2.post("/get_json_data")
async def upload_files_json(response: Response, documents: list[UploadFile] = File(...), user=Depends(login_manager_v2)):
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

        resultArr = []
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
                response_json = {"FileName" : document.filename, "Error": "Insufficient Credits"}
                resultArr.append(response_json)


        # Schedule the upload_files_to_queue task as a background task

        for Index ,file in enumerate(filenames):
            # print(file)
            result = store_pdf_data_v2(client,user_id,file,STATIC_DIR,ocrmodel)
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


def get_next_user_id():
    counter = mongo_conn.get_db()["Counter"].find_one_and_update(
        {"cntName": "userId"},  # This identifies the user counter
        {"$inc": {"sequence_value": 1}},  # Increment the sequence value by 1
        return_document=ReturnDocument.AFTER,  # Return the updated document after the increment
        upsert=True  # Create the counter document if it doesn't exist
    )
    return str(counter['sequence_value'])

class CreateUserRequest(BaseModel):
    company_name: str
    username: str
    password: str
    email: str
    # access_token: str = ""
    isAdmin: bool
    totalCredits: int = 0  # Default to 0 if not provided

@api_router_v2.post("/admin/create_user")
def create_user(response: Response, request: CreateUserRequest, current_user: dict = Depends(role_required(["admin"], login_manager_v2))):
    try:
        # Check if the username already exists
        existing_user = mongo_conn.get_users_collection().find_one({"username": request.username})
        if existing_user:
            response.status_code = 200
            response.body = json.dumps({"error": "username already exist"}).encode()
            return response
        # Create the new user data
        new_user = {
            "company_name": request.company_name,
            "username": request.username,
            "password": request.password,  # Make sure to hash the password in a real-world application
            # "access_token": request.access_token,
            "email": request.email,
            "role" : ["user"],
            "totalCredits": request.totalCredits,  # Initialize the total credits to the credit limit
            "createdAt": datetime.now(),
            "modifiedAt": datetime.now()
        }
        if(request.isAdmin):
            new_user["role"] = ["user", "admin"]

        user_id = get_next_user_id()
        new_user['userId'] = user_id

        # Insert the new user into the database
        mongo_conn.get_users_collection().insert_one(new_user)

        # Insert default fields for new user 
        mongo_conn.get_user_fields_collection().insert_one({"userId": user_id, "fields": _default_fields})

        response.status_code = 200
        response.body = json.dumps({"message": f"User '{request.username}' created successfully."}).encode()
        return response

    except Exception as e:
        # Handle any other exceptions
        response.status_code = 200
        response.body = json.dumps({"error": str(e)}).encode()
        return response


class Update_credits(BaseModel):
    username: str
    new_credits: int

@api_router_v2.post("/admin/update_credits")
def update_credits(response: Response, request: Update_credits, current_user: dict = Depends(role_required(["admin"], login_manager_v2))):
    try:
        # Check if the username already exists
        user = mongo_conn.get_users_collection().find_one({"username": request.username})
        if not user:
            response.status_code = 200
            response.body = json.dumps({"error": "coudn't find uesr with given username"}).encode()
            return response

        old_credits = user.get("totalCredits", 0)

        # Update the user's credits
        mongo_conn.get_users_collection().update_one(
            {"username": request.username},  # Filter to find the user by username
            {"$set": {"totalCredits": request.new_credits, "modifiedAt": datetime.now()}}  # Update total credits and modifiedAt fields
        )

        # Return a success response with old and new credits
        response.status_code = 200
        response.body = json.dumps({
            "message": f"User '{request.username}' credits updated successfully.",
            "old_credits": old_credits,
            "new_credits": request.new_credits
        }).encode()
        return response

    except Exception as e:
        # Handle any other exceptions
        response.status_code = 200
        response.body = json.dumps({"error": str(e)}).encode()
        return response
    

class Get_credits(BaseModel):
    username: str

@api_router_v2.get("/get_credits")
def get_credits(response: Response, request: Get_credits, current_user: dict = Depends(login_manager_v2)):
    try:
        # Check if the username already exists
        user = mongo_conn.get_users_collection().find_one({"username": request.username})
        if not user:
            response.status_code = 200
            response.body = json.dumps({"error": "coudn't find uesr with given username"}).encode()
            return response

        # Return a success response with old and new credits
        response.status_code = 200
        response.body = json.dumps({
            "message": f"User '{request.username}' credits fetched successfully.",
            "totalCredits": user["totalCredits"]
        }).encode()
        return response

    except Exception as e:
        # Handle any other exceptions
        response.status_code = 200
        response.body = json.dumps({"error": str(e)}).encode()
        return response