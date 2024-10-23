from doctr.io import Document
from .pdf_utils import Pdf_Utils as Base_Pdf_Utils

class Pdf_Utils(Base_Pdf_Utils):
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