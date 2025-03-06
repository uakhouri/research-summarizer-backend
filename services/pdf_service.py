import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

# If using Windows, set Tesseract path manually if needed:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a multi-page PDF. Uses OCR if necessary.
    """
    extracted_text = ""

    try:
        # Try extracting selectable text using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
                else:
                    print(f"[WARNING] Page {page_num + 1}: No selectable text found.")

    except Exception as e:
        print(f"[ERROR] PDFPlumber failed: {str(e)}")

    # If no selectable text is found, use OCR for scanned PDFs
    if not extracted_text.strip():
        print("[INFO] No selectable text found. Using OCR on all pages...")

        try:
            images = convert_from_path(pdf_path)
            for i, image in enumerate(images):
                print(f"[INFO] Processing page {i + 1}/{len(images)} with OCR...")

                # Convert image to OpenCV format (grayscale for better OCR)
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

                # Preprocessing (denoising + thresholding for better accuracy)
                _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # Extract text using Tesseract OCR
                ocr_text = pytesseract.image_to_string(image, lang="eng")
                extracted_text += ocr_text + "\n"

        except Exception as e:
            print(f"[ERROR] OCR extraction failed: {str(e)}")
            return f"Error extracting text: {str(e)}"

    print(f"[DEBUG] Total Extracted Text Length: {len(extracted_text)}")
    return extracted_text.strip() if extracted_text else "Error: No text found in PDF."
