import pdfplumber, re, os
from docx2pdf import convert
from zipfile import ZipFile

class Pdf_Utils:
    def get_pdf_data_from_pdfplumber(self, pdf_path):
        """
        Extract text data from a PDF file.

        Args:
        - pdf_path (str): The file path of the PDF from which to extract text.

        Returns:
        - str: The concatenated text extracted from all pages of the PDF.
        """
        try:
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
        except Exception as e:
            raise Exception(str(e))

    def get_cords_of_word(self, gpt_json_data: dict, pdf_path):
        """
        Get the coordinates of words from the PDF based on the GPT-3 extracted data.

        Args:
        - gpt_json_data (dict): The JSON data containing the extracted invoice information.
        - pdf_path (str): The file path of the PDF to search for the words.

        Returns:
        - list: A list of dictionaries containing the extracted data with coordinates for each page.
        """
        try:
            all_pages_data = [gpt_json_data]
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
        except Exception as e:
            raise Exception(f"Error getting cords of word: {str(e)}")

    def remove_comments_from_json(self, json_string: str):
        """
        Remove comments from a JSON string. Comments are assumed to start with '//' and extend to the end of the line.

        :param json_string: A string containing JSON data with potential comments.
        :return: A JSON string with comments removed.
        """
        try:
            # Find the indices of the first '{' and the last '}' to isolate the JSON object
            start_index = json_string.find('{')
            end_index = json_string.rfind('}')
            json_string = json_string[start_index:end_index+1]

            # Use a regular expression to remove comments starting with //
            json_string = re.sub(r'//.*?\n', '', json_string)
            return json_string
        except Exception as e:
            # Raise an exception if any error occurs during comment removal
            raise Exception(str(e))

    def convert_doc(self, filename, STATIC_DIR):
        """
        Convert a document file to PDF format.

        :param filename: Path to the input document file.
        :return: Filename of the converted PDF file.
        """

        try:
            # Construct the input and output paths
            input_path = os.path.join(STATIC_DIR, filename)
            output_filename = f"{os.path.splitext(filename)[0]}.pdf"
            output_path = os.path.join(STATIC_DIR, output_filename)

            # Convert the document file to PDF
            convert(input_path, output_path)

            # Remove the original document file
            os.remove(input_path)

            # Return the filename of the converted PDF file
            return output_filename
        except Exception as e:
            # Handle any errors that occur during conversion
            raise Exception(f"Error converting document: {e}")
            # return ''

    def get_total_pages_pdf(self, pdfPath):
        """
        Get the total number of pages in a PDF file.

        :param pdfPath: Path to the PDF file.
        :return: Total number of pages in the PDF file.
        """
        try:
            # Open the PDF file and count the number of pages
            with pdfplumber.open(pdfPath) as pdf:
                return len(pdf.pages)
        except Exception as e:
            # Handle any errors that occur while getting the page count
            raise Exception(f"Error getting total pages of pdf: {str(e)}")

    def get_docx_page_count(self, docx_fpath):
        """
        Get the total number of pages in a DOCX file by reading the document properties.

        :param docx_fpath: Path to the DOCX file.
        :return: Total number of pages in the DOCX file.
        """
        try:
            # Open the DOCX file as a zip archive
            docx_object = ZipFile(docx_fpath)

            # Read the document properties from 'docProps/app.xml'
            docx_property_file_data = docx_object.read('docProps/app.xml').decode()

            # Use a regular expression to extract the page count from the document properties
            page_count = re.search(r"<Pages>(\d+)</Pages>", docx_property_file_data).group(1)
            return int(page_count)
        except Exception as e:
            # Handle any errors that occur while getting the page count
            raise Exception(f"Error getting total pages of word file: {str(e)}")