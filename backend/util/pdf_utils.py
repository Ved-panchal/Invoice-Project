import pdfplumber, re, os
from docx2pdf import convert
from doctr.io import Document
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
            docx_object = ZipFile(docx_fpath)
            docx_property_file_data = docx_object.read('docProps/app.xml').decode()
            page_count = re.search(r"<Pages>(\d+)</Pages>", docx_property_file_data).group(1)
            return int(page_count)
        except Exception as e:
            raise Exception(f"Error getting total pages of word file: {str(e)}")

    def find_cords_from_doctr(self, data,search_phrase, concatenated_text, pdf_height, pdf_width):
        try:
            if(search_phrase == "" or concatenated_text == ''):
                return []
            start_indices = []
            start_pos = concatenated_text.find(search_phrase)
            while start_pos != -1:
                start_indices.append(start_pos)
                start_pos = concatenated_text.find(search_phrase, start_pos + 1)
            results = []
            for start_index in start_indices:
                words_before_phrase = concatenated_text[:start_index].count(' ')
                phrase_word_count = len(search_phrase.split())
                phrase_data = data[words_before_phrase:words_before_phrase + phrase_word_count]
                bounding_boxes = [entry['bbox'] for entry in phrase_data]
                if bounding_boxes != []:
                    pdfplumber_format = {
                        "text": search_phrase,
                        "x0": min([bbox[0][0] for bbox in bounding_boxes]) * pdf_width / 2,
                        "top": min([bbox[0][1] for bbox in bounding_boxes]) * pdf_height / 2,
                        "x1": max([bbox[1][0] for bbox in bounding_boxes]) * pdf_width / 2,
                        "bottom": max([bbox[1][1] for bbox in bounding_boxes]) * pdf_height / 2
                    }
                    results.append(pdfplumber_format)
            return results
        except Exception as e:
            print("error searching in doctr data", e)
            return []

    def get_cords_of_word_v2(self, gpt_json_data: dict, result: Document) -> list:
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
            for page in result.pages:
                (pdf_height, pdf_width) = page.dimensions
                data = []
                text_with_cords = {}
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            data.append({
                                'text': word.value,
                                'bbox': word.geometry,
                            })
                concatenated_text = " ".join([entry['text'] for entry in data])
                # print("###########################################concatenated_text#########################################################")
                # print(concatenated_text)
                # print(f"page {page.dimensions} ,\n data {data}")
                # print("####################################################################################################################")
                for key, value in gpt_json_data.items():
                    if key in not_include_keys:
                        continue
                    if isinstance(value, list):
                        text_with_cords[key] = []
                        for item in value:
                            for k, v in item.items():
                                cord_list = self.find_cords_from_doctr(data, v, concatenated_text,pdf_height, pdf_width)
                                text_with_cords[key].append({"value": v, "cords": cord_list})
                                break
                    else:
                        cord_list = self.find_cords_from_doctr(data, value, concatenated_text,pdf_height, pdf_width)
                        text_with_cords[key] = {"value": value, "cords": cord_list}
                all_pages_data.append(text_with_cords)
            return all_pages_data
        except Exception as e:
            raise Exception(f"Error getting cords of word: {str(e)}")