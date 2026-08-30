import pytesseract
from PIL import Image

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Open image
image = Image.open("C:\Users\Thiru\Documents\ocr\image.png")

# Extract text
text = pytesseract.image_to_string(image)

# Print extracted text
print(text)