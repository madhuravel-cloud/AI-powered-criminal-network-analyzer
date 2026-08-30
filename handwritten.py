import cv2
import easyocr

# Read image
img = cv2.imread("image.jpg")

# Make sure image was loaded
if img is None:
    print("Could not find image.jpg")
    exit()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Improve contrast
gray = cv2.resize(gray, None, fx=2, fy=2)

# Save processed image
cv2.imwrite("processed.jpg", gray)

# OCR
reader = easyocr.Reader(['en'], gpu=False)

result = reader.readtext(
    "processed.jpg",
    detail=1,
    paragraph=True
)

for item in result:
    print(item[1])