import os
import re
import cv2
import easyocr

# Initialize the reader at the module level.
# This ensures the model weights are loaded into the 6GB VRAM only once,
# no matter how many times your teammates call the function below.
print("Loading EasyOCR models into VRAM...")
reader = easyocr.Reader(['en','hi'], gpu=True)

def extract_and_clean_text(image_path):
    """
    Extracts text from an evidence image, upscales it for better accuracy on small fonts,
    and cleans up common OCR typos.
    
    Args:
        image_path (str): The path to the image file.
        
    Returns:
        list: A list of dictionaries containing 'text', 'confidence', and 'box'.
    """
    if not os.path.exists(image_path):
        print(f"Error: Could not find '{image_path}'")
        return []

    # 1. Preprocess: Read and upscale the image by 2x for better small-text accuracy
    img = cv2.imread(image_path)
    upscaled_img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # 2. Extract text using the globally loaded reader
    raw_results = reader.readtext(upscaled_img, detail=1)
    
    # 3. Post-process Setup: Typos and Hindi numerals
    hindi_to_eng = str.maketrans({
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    })
    common_typos = {
        "Ollicer": "Officer", "ollicer": "officer", "thal": "that",
        "faithlully": "faithfully", "2\"d": "2nd", "2\"": "2nd"
    }
    
    cleaned_records = []
    
    # 4. Clean and format the results
    for (bbox, text, confidence) in raw_results:
        # Strip stray quotes
        cleaned_text = re.sub(r"^['\"`]+", "", text).strip()
        
        # Fix known typos
        for wrong, right in common_typos.items():
            cleaned_text = cleaned_text.replace(wrong, right)
            
        # Convert any Hindi numerals to standard
        cleaned_text = cleaned_text.translate(hindi_to_eng)
        
        if not cleaned_text:
            continue
            
        # Scale the bounding box coordinates back to the original image size
        original_bbox = [
            [int(pt[0] / 2.0), int(pt[1] / 2.0)]
            for pt in bbox
        ]
        
        cleaned_records.append({
            "text": cleaned_text,
            "confidence": round(float(confidence), 2),
            "box": original_bbox
        })
        
    return cleaned_records