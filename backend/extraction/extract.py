from together import Together
from fastapi import HTTPException
from bson import ObjectId
import json, os

from logger import logger
from models import TextData, PDFUploadStatus
from util import pdf_utils
from .prompt import generate_dynamic_prompt, _default_fields
from database import mongo_conn

@logger.catch
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
        logger.info('Qwen task received.')
        # For dynamic prompt, frontend left
        fields = mongo_conn.get_user_fields_collection().find_one({"userId": user_id}, {"fields": 1, "_id": 0})
        if fields is not None:
            fields = fields["fields"]
        else:
            fields = _default_fields

        prompt = generate_dynamic_prompt(text, fields)
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="Qwen/Qwen1.5-110B-Chat",
            messages=messages,
            temperature=0
        )
        logger.info('Qwen response sent.')
        return str(response.choices[0].message.content)

    except Exception as e:
        logger.exception("Exception in _get_data_from_gpt")
        raise Exception(str(e))

@logger.catch
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
    if not pdf_path:
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        pdf_data = pdf_utils.get_pdf_data_from_pdfplumber(pdf_path)
        logger.info('Received data from PdfPlumber.')
        result = _get_data_from_gpt(client, pdf_data, user_id)
        logger.info('Received response from Qwen.')
        if result:
            extracted_text = pdf_utils.remove_comments_from_json(result)
            json_data = json.loads(extracted_text)
            res_list = pdf_utils.get_cords_of_word(json_data, pdf_path)
            # res_list.insert(0, json_data)
            return res_list
        else:
            raise Exception('Could not fetch data from API.')
    except Exception as e:
        logger.exception("Error in _get_invoice_data_text")
        raise HTTPException(status_code=500, detail=str(e))

@logger.catch
def _process_file(client, filename: str, user_id: str) -> str:
    """
    Process the provided file and extract invoice data.

    Args:
    - client : Object of Open AI or Qwen or other AI you are using.
    - filename : The name of the file to be processed.
    - user_id : The ID of the user.

    Returns:
    - str: The ID of the inserted data record.

    Raises:
    - HTTPException: If the file format is unsupported or if there is a database insertion error.
    """
    try:
        file_ext = filename.split('.')[-1].lower()
        if file_ext == 'pdf':
            logger.info('Task sent for data extraction.')
            json_data = _get_invoice_data_text(client, f"./static/{user_id}/{filename}", user_id)
            logger.info('Received data for extraction.')
            data = {'data': json_data}
            pdf_data_col = mongo_conn.get_pdf_data_collection()
            result = pdf_data_col.insert_one(data)
            logger.info('Received data inserted into PdfData collection.')
            if result:
                result = str(result.inserted_id) + "0"
            else:
                raise HTTPException(status_code=400, detail="Database insertion error")
            return result
        else:
            raise HTTPException(status_code=400, detail='Unsupported file format')
    except Exception as e:
        logger.exception("Error in _process_file")
        raise Exception(str(e))

@logger.catch
def _store_pdf_data(client, user_id, filename: str, STATIC_DIR):
    """
    Store the processed PDF data and update the database.

    Args:
    - client : Object of Open AI or Qwen or other AI you are using.
    - user_id : The ID of the user.
    - filename : The name of the file to be stored.
    - STATIC_DIR : The directory where static files are stored.

    Returns:
    - str: The new file ID.

    Raises:
    - Exception: If there is an error during processing or database update.
    """
    try:
        file_id = filename.split('.')[0]
        obj_id = ObjectId(file_id)

        file_ext = filename.split('.')[-1].lower()
        if file_ext in ['doc', 'docx']:
            filename = pdf_utils.convert_doc(filename)

        file_ext = filename.split('.')[-1]
        file_location = STATIC_DIR / user_id / filename

        logger.info('Sent Pdf for processing.')
        new_file_id = _process_file(client, filename, user_id)
        logger.info('Received new pdf id after processing.')

        # Construct new filename using file_id and the original extension
        new_filename = f"{new_file_id}.{file_ext}"
        new_file_location = STATIC_DIR / user_id / new_filename

        # Rename the file
        os.rename(file_location, new_file_location)
        logger.info('Pdf renamed in static folder.')

        update_operation = {
            '$set': {
                'pdfData.pdfId': new_file_id,
                'pdfData.pdfStatus': PDFUploadStatus.COMPLETED
            }
        }
        pdf_mapping = mongo_conn.get_user_pdf_mapping_collection()
        pdf_mapping.update_one({'_id': obj_id}, update_operation)
        logger.info('New pdfId with status as Completed updated to UserPdfMapping collection.')

        return new_file_id

    except Exception as e:
        logger.exception("Error in _store_pdf_data")
        update_operation = {
            '$set': {
                'pdfData.pdfId': '',
                'pdfData.pdfStatus': PDFUploadStatus.EXCEPTION
            }
        }
        pdf_mapping = mongo_conn.get_user_pdf_mapping_collection()
        pdf_mapping.update_one({'_id': obj_id}, update_operation)
        logger.info('New pdfId with status as Exception updated to UserPdfMapping collection.')
        raise Exception("Exception from store_pdf_data: " + str(e))

@logger.catch
def _get_pdf_name(user_id: str, invoice_id: str) -> str:
    """
    Find the PDF name given the user ID and invoice ID.

    Args:
    - user_id (str): The user ID.
    - invoice_id (str): The invoice ID.

    Returns:
    - str: The PDF name.

    Raises:
    - HTTPException: If the PDF is not found.
    """
    pdf = mongo_conn.get_user_pdf_mapping_collection().find_one({"pdfData.pdfId": invoice_id, "userId": user_id}, {"pdfData.pdfName": 1, "_id": 0})
    if pdf:
        return pdf['pdfData']['pdfName']
    raise HTTPException(status_code=404, detail="PDF not found")
