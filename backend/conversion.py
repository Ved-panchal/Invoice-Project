from PIL import Image
import os
from docx2pdf import convert

async def convert_image(filename, output_format='JPEG') -> str:
    """
    Convert an image to a specified format and save it.

    :param filename: Path to the input image.
    :param output_format: Format to convert the image to (default is 'JPEG').
    """
    input_path = os.path.join('static', filename)
    output_file_name = f"{os.path.splitext(filename)[0]}.JPEG"
    output_path = os.path.join('static', output_file_name)

    try:
        with Image.open(input_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path, format=output_format)
            os.remove(input_path)
        filename = filename.split('.')
        filename[-1] = 'JPEG'
        return '.'.join(filename)
    except Exception as e:
        print(f"Error converting image: {e}")
        return ''
    

async def convert_doc(filename):
    """
    Convert a document file to PDF format.

    :param filename: Path to the input document file.
    :return: Filename of the converted PDF file.
    """
    # Construct the input and output paths
    input_path = os.path.join('static', filename)
    output_filename = f"{os.path.splitext(filename)[0]}.pdf"
    output_path = os.path.join('static', output_filename)

    try:
        # Convert the document file to PDF
        convert(input_path, output_path)

        # Remove the original document file
        os.remove(input_path)

        # Return the filename of the converted PDF file
        return output_filename
    except Exception as e:
        # Handle any errors that occur during conversion
        print(f"Error converting document: {e}")
        return ''
