import pytesseract, json, cv2
from app.config import settings
from .preprocess import preprocess

def ocr_image(path: str):
 img = cv2.imread(path)
 if img is None:
     return "", {"error": "Could not load image"}
 
 proc = preprocess(img)
 
 # Enhanced Tesseract configuration for betting slips
 custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,+-%@:()[]/ '
 
 try:
     # Primary OCR with custom config
     data = pytesseract.image_to_data(proc, output_type=pytesseract.Output.DICT, config=custom_config)
     lines = []
     for i, txt in enumerate(data["text"]):
         if txt and txt.strip():
             lines.append(txt.strip())
     
     text_result = "\n".join(lines)
     
     # If primary OCR fails or produces very little text, try alternative PSM
     if len(text_result.strip()) < 10:
         alt_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,+-%@:()[]/ '
         alt_data = pytesseract.image_to_data(proc, output_type=pytesseract.Output.DICT, config=alt_config)
         alt_lines = []
         for i, txt in enumerate(alt_data["text"]):
             if txt and txt.strip():
                 alt_lines.append(txt.strip())
         
         alt_result = "\n".join(alt_lines)
         if len(alt_result.strip()) > len(text_result.strip()):
             return alt_result, alt_data
     
     return text_result, data
     
 except Exception as e:
     return f"OCR Error: {str(e)}", {"error": str(e)}
