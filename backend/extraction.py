from prompt import prepare_prompt
from openai import OpenAI
from fastapi import HTTPException
from models import DataType, ImageUrls, TextData
from pdf_utils import get_cords_of_word, get_pdf_data_from_pdfplumber,remove_comments_from_json
from conversion import convert_doc
import json, os
from database_collections import MongoDBConnection

mongo_client = MongoDBConnection()
user_pdf_mapping_collection = mongo_client.get_user_pdf_mapping_collection()

def get_data_from_gpt(data_type: DataType, client: OpenAI, text):
    """
    Extract invoice data using OpenAI API based on the data type.

    Args:
    - data_type (DataType): The type of data (IMAGEURL or TEXT).
    - text (Union[str, List[str]]): The text extracted from PDF or list of image URLs.

    Returns:
    - str: The extracted invoice data in JSON format.
    """
    if data_type == DataType.IMAGEURL:
        prompt = prepare_prompt()
        messages = [{"role": "user", "content": [prompt]}]
        for url in text:
            messages[0]["content"].append({"type": "image_url", "image_url": {"url": url}})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0
        )
    else:
        prompt = prepare_prompt(text)
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="Qwen/Qwen1.5-110B-Chat",
            messages=messages,
            temperature=0
        )
    return response.choices[0].message.content

async def get_invoice_data(client: OpenAI, image_urls) -> dict:
    """
    API endpoint to extract invoice data from image URLs.

    Args:
    - image_urls (ImageUrls): A list of image URLs containing invoice images.

    Returns:
    - dict: The extracted invoice data in JSON format.

    Raises:
    - HTTPException: If no image URLs are provided or an error occurs during processing.
    """
    if not image_urls:
        raise HTTPException(status_code=400, detail="No image URLs provided")

    try:
        result = get_data_from_gpt(DataType.IMAGEURL, client, image_urls)
        start_index = result.find('{')
        end_index = result.rfind('}')
        extracted_text = result[start_index:end_index+1]
        json_response = json.loads(extracted_text)
        return json_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_invoice_data_text(client, pdf_path: TextData) -> list:
    """
    API endpoint to extract invoice data from text extracted from a PDF.

    Args:
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
        pdf_data = get_pdf_data_from_pdfplumber(pdf_path)
        # print(pdf_data)
        result = get_data_from_gpt(DataType.TEXT, client, pdf_data)
        if result:
            extracted_text = remove_comments_from_json(result)
            # print("extracted_text: ", extracted_text)
            json_data = json.loads(extracted_text)
            # print("json_data: ", json_data)
            res_list = get_cords_of_word(json_data, pdf_path)
            res_list.insert(0, json_data)
            return res_list
        else:
            print('Could not fetch data from API.')
    except Exception as e:
        print("Error requesting api from extraction/get_invoice_data_text.\n",e)
        raise HTTPException(status_code=500, detail=str(e))
    
def process_file(client, pdf_data_collection, filename: str, user_id: str) -> str:
    file_ext = filename.split('.')[-1].lower()
    if file_ext == 'pdf':
        json_data =  get_invoice_data_text(client, f"./static/{user_id}/{filename}")
        data = {'data' : json_data}
        result = pdf_data_collection.insert_one(data)
        if result:
            result = str(result.inserted_id) + "0"
        else:
            raise HTTPException(status_code=400, detail="Database insertion error")
        return result

    # elif file_ext == "jpeg":
    #     if filename:
    #         (uploaded_image_urls, _) = await process_image(filename)
    #         json_data = await get_invoice_data(client, uploaded_image_urls)
    #         data = {'data' : [json_data]}
    #         result = pdf_data_collection.insert_one(data)
    #         if result:
    #             result = str(result.inserted_id) + "1"
    #         else:
    #             raise HTTPException(status_code=400, detail="Database insertion error")
    #         return result
    #     else:
    #         raise HTTPException(status_code=400, detail="Can not convert image to JPEG")
    else:
        raise HTTPException(status_code=400, detail='Unsupported file format')
    
def store_pdf_data(client, user_id, filename, STATIC_DIR):
    file_ext = filename.split('.')[-1].lower()
    if file_ext in ['doc', 'docx']:
        filename = convert_doc(filename)

            # elif file_ext in ['jpg', 'jpeg', 'png', 'tiff']:
            #     filename = await convert_image(filename)

    file_id = process_file(client, user_pdf_mapping_collection, filename, user_id)
    file_ext = filename.split('.')[-1]
    file_location = STATIC_DIR / user_id / filename

            # Construct new filename using file_id and the original extension
    new_filename = f"{file_id}.{file_ext}"
    new_file_location = STATIC_DIR / user_id / new_filename

            # Rename the file
    os.rename(file_location, new_file_location)
    return file_id
