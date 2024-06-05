from prompt import prepare_prompt
from openai import OpenAI
from fastapi import HTTPException
from models import DataType, ImageUrls, TextData
from pdf_utils import get_cords_of_word, extract_invoice_data_pdf
import json

def extract_invoice_data(data_type: DataType, client: OpenAI, text):
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
            model="gpt-3.5-turbo",
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
        result = extract_invoice_data(DataType.IMAGEURL, client, image_urls)
        start_index = result.find('{')
        end_index = result.rfind('}')
        extracted_text = result[start_index:end_index+1]
        json_response = json.loads(extracted_text)
        return json_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_invoice_data_text(client: OpenAI, pdf_path: TextData) -> list:
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
        pdf_data = extract_invoice_data_pdf(pdf_path)
        result = extract_invoice_data(DataType.TEXT, client, pdf_data)
        json_data = json.loads(result)
        res_list = get_cords_of_word(json_data, pdf_path)
        res_list.insert(0, json_data)
        return res_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))