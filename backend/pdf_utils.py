import pdfplumber, os, requests, tempfile, json

def extract_invoice_data_pdf(pdf_path):
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
            # Extract text from each page with specific tolerances and densities.
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
