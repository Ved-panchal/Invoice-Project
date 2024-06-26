from together import Together
from fastapi import HTTPException
from models import TextData
import json, os
from bson import ObjectId

from util import pdf_utils
from .prompt import generate_dynamic_prompt, _default_fields
from database import mongo_conn

def _get_data_from_gpt(client: Together, text, user_id: str) -> str:
    """
    Extract invoice data using OpenAI API based on the data type.

    Args:
    - data_type (DataType): The type of data (IMAGEURL or TEXT).
    - text (Union[str, List[str]]): The text extracted from PDF or list of image URLs.

    Returns:
    - str: The extracted invoice data in JSON format.
    """
    try:
        # For dynamic prompt, frontend left
        fields = mongo_conn.get_user_fields_collection().find_one({"userId": user_id}, {"fields": 1, "_id": 0})
        if fields is not None:
            fields = fields["fields"]
        else :
            fields = _default_fields
        print("fields", fields)
        prompt = generate_dynamic_prompt(text, fields)
        print("prompt", prompt)
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="Qwen/Qwen1.5-110B-Chat",
            messages=messages,
            temperature=0
        )
        return str(response.choices[0].message.content)
    
    except Exception as e:
        raise Exception(str(e))

def _get_invoice_data_text(client, pdf_path: TextData, user_id: str) -> list:
    """
    API endpoint to extract invoice data from text extracted from a PDF.

    Args:
    - client : Object of Open AI or Qwen or other AI you are using.
    - pdf_path : The path to the PDF file.

    Returns:
    - list: A list containing the extracted invoice data in JSON format and the coordinates of the extracted words.

    Raises:
    - HTTPException: If no text is provided or an error occurs during processing.
    """
    # pdf_path = data.pdf_path
    if not pdf_path:
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        pdf_data = pdf_utils.get_pdf_data_from_pdfplumber(pdf_path)
        # print(pdf_data)
        result = _get_data_from_gpt(client, pdf_data, user_id)
        if result:
            extracted_text = pdf_utils.remove_comments_from_json(result)
            # print("extracted_text: ", extracted_text)
            json_data = json.loads(extracted_text)
            # print("json_data: ", json_data)
            res_list = pdf_utils.get_cords_of_word(json_data, pdf_path)
            res_list.insert(0, json_data)
            return res_list
        else:
            raise Exception('Could not fetch data from API.')
    except Exception as e:
        print("Error requesting api from extraction/get_invoice_data_text.\n",e)
        raise HTTPException(status_code=500, detail=str(e))
    
def _process_file(client, filename: str, user_id: str) -> str:
    try:
        file_ext = filename.split('.')[-1].lower()
        if file_ext == 'pdf':
            json_data =  _get_invoice_data_text(client, f"./static/{user_id}/{filename}", user_id)
            data = {'data' : json_data}
            pdf_data_col = mongo_conn.get_pdf_data_collection()
            result = pdf_data_col.insert_one(data)
            if result:
                result = str(result.inserted_id) + "0"
            else:
                raise HTTPException(status_code=400, detail="Database insertion error")
            return result
        else:
            raise HTTPException(status_code=400, detail='Unsupported file format')
    except Exception as e:
        raise Exception(str(e))
    
def _store_pdf_data(client, user_id, filename: str, STATIC_DIR):
    try:
        file_id = filename.split('.')[0]
        obj_id = ObjectId(file_id)

        file_ext = filename.split('.')[-1].lower()
        if file_ext in ['doc', 'docx']:
            filename = pdf_utils.convert_doc(filename)

                # elif file_ext in ['jpg', 'jpeg', 'png', 'tiff']:
                #     filename = await convert_image(filename)

        file_ext = filename.split('.')[-1]
        file_location = STATIC_DIR / user_id / filename

        new_file_id = _process_file(client, filename, user_id)

        # Construct new filename using file_id and the original extension
        new_filename = f"{new_file_id}.{file_ext}"
        new_file_location = STATIC_DIR / user_id / new_filename

        # Rename the file
        os.rename(file_location, new_file_location)

        update_operation = {
            '$set': {
                'pdfData.pdfId': new_file_id,
                'pdfData.pdfStatus': 'Completed'
            }
        }
        pdf_mapping = mongo_conn.get_user_pdf_mapping_collection()
        pdf_mapping.update_one({'_id':obj_id}, update_operation)

        return new_file_id

    except Exception as e:
        update_operation = {
            '$set': {
                'pdfData.pdfId': '',
                'pdfData.pdfStatus': 'Exception'
            }
        }
        pdf_mapping = mongo_conn.get_user_pdf_mapping_collection()
        pdf_mapping.update_one({'_id':obj_id}, update_operation)
        raise Exception("Exception from store_pdf_data: ", str(e))
