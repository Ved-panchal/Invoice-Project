from together import Together
from fastapi import HTTPException
from bson import ObjectId
import json, os

from logger import logger
from models import TextData, PDFUploadStatus
from util import pdf_utils
from .prompt import generate_dynamic_prompt, _default_fields
from database import mongo_conn

from doctr.io import DocumentFile
from doctr.models.predictor.tensorflow import OCRPredictor

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
def _get_invoice_data_text(client, pdf_path: TextData, user_id: str, ocrmodel: OCRPredictor) -> list:
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
        flag = True
        pdf_data = pdf_utils.get_pdf_data_from_pdfplumber(pdf_path)
        if pdf_data=="":
            doc = DocumentFile.from_pdf(pdf_path)
            result = ocrmodel(doc)
            flag = False
            pdf_data = result.render()
        
        logger.info('Received data from PdfPlumber.')
        gpt_result = _get_data_from_gpt(client, pdf_data, user_id)
        print(f'gpt_result: {gpt_result}')
        logger.info('Received response from Qwen.')
        if gpt_result:
            extracted_text = pdf_utils.remove_comments_from_json(gpt_result)
            json_data = json.loads(extracted_text)
            print(f'json_data: {json_data}')
            if flag:
                res_list = pdf_utils.get_cords_of_word(json_data, pdf_path)
            else:
                res_list = pdf_utils.get_cords_of_word_v2(json_data,result)

            # print("####################################################################################################################")
            # print(res_list, " falg ", flag)
            # print("####################################################################################################################")
            return res_list
        else:
            raise Exception('Could not fetch data from API.')
    except Exception as e:
        logger.exception("Error in _get_invoice_data_text")
        raise HTTPException(status_code=500, detail=str(e))

@logger.catch
def _process_file(client, filename: str, user_id: str, ocrmodel: OCRPredictor) -> str:
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
            json_data = _get_invoice_data_text(client, f"./static/{user_id}/{filename}", user_id, ocrmodel)
            logger.info('Received data for extraction.')
            data = {'data': json_data}
            pdf_data_col = mongo_conn.get_pdf_data_collection()
            result = pdf_data_col.insert_one(data)
            logger.info('Received data inserted into PdfData collection.')
            if result:
                result = [str(result.inserted_id) + "0", json_data[0]]
            else:
                raise HTTPException(status_code=400, detail="Database insertion error")
            return result
        else:
            raise HTTPException(status_code=400, detail='Unsupported file format')
    except Exception as e:
        logger.exception("Error in _process_file")
        raise Exception(str(e))

@logger.catch
def update_pdf_status(obj_id, new_file_id, pdfUploadStatus):
    try:
        update_operation = {
            '$set': {
                'pdfData.pdfId': new_file_id,
                'pdfData.pdfStatus': pdfUploadStatus
            }
        }

        mongo_conn.get_user_pdf_mapping_collection().update_one({'_id': obj_id}, update_operation)
        logger.info('New pdfId with status as Completed updated to UserPdfMapping collection.')
    except Exception as e:
        raise Exception("Exception from updating pdf status: " + str(e))

@logger.catch
def update_credits(user_id, total_pages):
    try:
        update_credits = {
            '$inc': {
                'totalCredits': -total_pages
            }
        }

        mongo_conn.get_users_collection().update_one({"userId": user_id}, update_credits)
    except Exception as e:
        raise Exception("Exception from updating credits: " + str(e))


############### check pdf path, json error -> check data ######################

@logger.catch
def _store_pdf_data(client, user_id, filename: str, STATIC_DIR,ocrmodel : OCRPredictor):
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
            filename = pdf_utils.convert_doc(filename, STATIC_DIR / user_id)

        file_ext = filename.split('.')[-1]
        file_location = STATIC_DIR / user_id / filename

        # Get the total number of pages in the PDF
        total_pages = pdf_utils.get_total_pages_pdf(file_location)
        logger.info(f'Total pages in the PDF: {total_pages}')

        logger.info('Sent Pdf for processing.')
        [new_file_id, json_data] = _process_file(client, filename, user_id, ocrmodel)
        logger.info('Received new pdf id after processing.')

        # Construct new filename using file_id and the original extension
        new_filename = f"{new_file_id}.{file_ext}"
        new_file_location = STATIC_DIR / user_id / new_filename

        # Rename the file
        os.rename(file_location, new_file_location)
        logger.info('Pdf renamed in static folder.')

        # Update pdf status
        update_pdf_status(obj_id, new_file_id, PDFUploadStatus.COMPLETED)

        # Subtract total_pages from totalCredits ensuring it does not go below 0
        update_credits(user_id, total_pages)

        return [new_file_id, total_pages, json_data]
    except Exception as e:
        logger.exception("Error in _store_pdf_data")
        update_pdf_status(obj_id, '', PDFUploadStatus.EXCEPTION)
        logger.info('New pdfId with status as Exception updated to UserPdfMapping collection.')
        raise Exception("Exception from store_pdf_data: " + str(e))
