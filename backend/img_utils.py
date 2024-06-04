import cv2
import cloudinary, cloudinary.uploader
from io import BytesIO
from PIL import Image
import numpy as np

def upload_image_to_cloudinary(image_np, filename, page_number):
    """
    Upload an image to Cloudinary.

    Args:
    - image_np (numpy.ndarray): The image in NumPy array format.
    - filename (str): The base filename for the image.
    - page_number (int): The page number of the image.

    Returns:
    - str: The URL of the uploaded image.
    """
    # Encode the image as JPEG
    _, img_encoded = cv2.imencode('.jpg', image_np)
    
    # Convert the encoded image to BytesIO object
    img_io = BytesIO(img_encoded)
    img_io.name = f'image{page_number+1}.jpg'
    
    # Upload the image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        img_io,
        folder='output_images',
        public_id=f'{filename}/image{page_number+1}'
    )
    
    # Return the URL of the uploaded image
    return upload_result['url']

async def process_image(filename):
    """
    Process an image file, convert it to grayscale, and upload it to Cloudinary.

    Args:
    - filename (str): The file path of the image to process.

    Returns:
    - list: A list containing the URL of the uploaded image.
    - str: A message indicating success or failure.
    """
    try:
        # Open the image file
        image = Image.open(f"static/{filename}")
    except Exception as e:
        return [], f"Error opening image: {e}"
    
    if not image:
        return [], "Failed to open image"
    
    # Convert the image to NumPy array and grayscale
    image_np = np.array(image.convert('L'))
    
    # Upload the grayscale image to Cloudinary
    uploaded_image_urls = upload_image_to_cloudinary(image_np, filename, 0)
    
    return [uploaded_image_urls], "Image processed and uploaded successfully"
