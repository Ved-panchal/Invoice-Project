import pdfplumber, pymupdf, cv2, re
import numpy as np
from img_utils import upload_image_to_cloudinary

def get_pdf_data_from_pdfplumber(pdf_path):
    """
    Extract text data from a PDF file.

    Args:
    - pdf_path (str): The file path of the PDF from which to extract text.

    Returns:
    - str: The concatenated text extracted from all pages of the PDF.
    """
    data = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            data += page.extract_text(
                x_tolerance=3,
                x_tolerance_ratio=None,
                y_tolerance=3,
                layout=False,
                x_density=7.25,
                y_density=13,
                line_dir_render=None,
                char_dir_render=None
            )
    return data

def get_cords_of_word(gpt_json_data: dict, pdf_path):
    """
    Get the coordinates of words from the PDF based on the GPT-3 extracted data.

    Args:
    - gpt_json_data (dict): The JSON data containing the extracted invoice information.
    - pdf_path (str): The file path of the PDF to search for the words.

    Returns:
    - list: A list of dictionaries containing the extracted data with coordinates for each page.
    """
    all_pages_data = []
    not_include_keys = ['DiscountPercent', 'Quantity', 'TaxCode', 'UnitPrice']
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text_with_cords = {}
            for key, value in gpt_json_data.items():
                if key in not_include_keys:
                    continue
                if isinstance(value, list):
                    text_with_cords[key] = []
                    for item in value:
                        for k, v in item.items():
                            data = page.search(
                                v,
                                regex=False,
                                case=True,
                                return_chars=False,
                                return_groups=False
                            )
                            text_with_cords[key].append({"value": v, "cords": data})
                            break
                else:
                    data = page.search(
                        value,
                        regex=False,
                        case=True,
                        return_chars=False,
                        return_groups=False
                    )
                    text_with_cords[key] = {"value": value, "cords": data}
            all_pages_data.append(text_with_cords)
    return all_pages_data


def process_pdf(pdf_path, output_folder, filename):
    """
    Process a PDF file, extract images from each page, and upload them.

    Args:
    - pdf_path (str): The file path of the PDF to process.
    - output_folder (str): The folder to save the uploaded images.
    - filename (str): The base filename for the images.

    Returns:
    - list: A list of URLs of the uploaded images.
    """
    pdf_document = pymupdf.open(pdf_path)
    uploaded_image_urls = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        # Set the zoom level
        mat = pymupdf.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        # Convert to a numpy array
        image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        if image_np.shape[2] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)

        # Upload the image to Cloudinary
        uploaded_image_urls.append(upload_image_to_cloudinary(image_np, filename, page_number))

    pdf_document.close()
    return uploaded_image_urls


def remove_comments_from_json(json_string):
    start_index = json_string.find('{')
    end_index = json_string.rfind('}')
    json_string = json_string[start_index:end_index+1]

    # Use a regular expression to remove comments starting with //
    json_string = re.sub(r'//.*?\n', '', json_string)
    return json_string