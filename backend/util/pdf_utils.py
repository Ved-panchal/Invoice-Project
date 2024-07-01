import pdfplumber, re, os
from docx2pdf import convert

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

    def remove_comments_from_json(self, json_string: str):
        try:
            start_index = json_string.find('{')
            end_index = json_string.rfind('}')
            json_string = json_string[start_index:end_index+1]

            # Use a regular expression to remove comments starting with //
            json_string = re.sub(r'//.*?\n', '', json_string)
            return json_string
        except Exception as e:
            raise Exception(str(e))

    def convert_doc(self, filename):
        """
        Convert a document file to PDF format.

        :param filename: Path to the input document file.
        :return: Filename of the converted PDF file.
        """

        try:
            # Construct the input and output paths
            input_path = os.path.join('static', filename)
            output_filename = f"{os.path.splitext(filename)[0]}.pdf"
            output_path = os.path.join('static', output_filename)

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
