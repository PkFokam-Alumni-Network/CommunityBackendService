import base64, io
from PIL import Image, ImageDraw

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB

# the image received from the client is a base64 encoded string
def validate_image(base64_image: str) -> str:
    if base64_image.startswith('data:image'):
        base64_data = base64_image.split(",")[1]
    else:
        raise ValueError("Invalid base64 image format")

    try:
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        raise ValueError(f"Error decoding base64 data: {str(e)}")

    image_file = io.BytesIO(image_data)
    
    try:
        with Image.open(image_file) as img:
            img_format = img.format.lower()
            allowed_formats = ["jpeg", "png", "jpg"]
            if img_format not in allowed_formats:
                raise ValueError("Invalid file type. Only JPEG, JPG, PNG images are allowed.")
            
            image_file.seek(0, io.SEEK_END)  
            file_size = image_file.tell()
            if file_size > MAX_FILE_SIZE:
                raise ValueError(f"File is too large. Maximum size allowed is {MAX_FILE_SIZE / (1024 * 1024)}MB.")
            
            # Reset pointer to the beginning of the file for further operations if needed
            image_file.seek(0)
            return img_format
    
    except IOError:
        raise ValueError("Unable to open the image. The file may not be a valid image.")

def crop_image_to_circle(image_data: io.BytesIO) -> io.BytesIO:
    image = Image.open(image_data).convert("RGBA")
    
    width, height = image.size
    min_dim = min(width, height)
    
    # Crop to a square (centered crop)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    
    image = image.crop((left, top, right, bottom))
    
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    draw.ellipse((0, 0, min_dim, min_dim), fill=255)
    
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask=mask)
    
    output = io.BytesIO()
    result.save(output, format="PNG")  # Save as PNG to preserve transparency
    output.seek(0)
    
    return output
    
def decode_base64_image(base64_image: str):
    if base64_image.startswith('data:image'):
        base64_data = base64_image.split(",")[1]
    else:
        raise ValueError("Invalid base64 image format")
    try:
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        raise ValueError(f"Error decoding base64 data: {str(e)}")

    return io.BytesIO(image_data)