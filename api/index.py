from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageFilter, ImageEnhance
from pytesseract import image_to_string
from PIL import Image
import fitz
import io
import re
import json
import numpy as np
app = Flask(__name__)
#CORS(app)

# ...existing code...

@app.route("/api/processbill")
def process_bill():
    if request.method == "GET":
        img_path = request.url.split("?image=")[1]

        def preprocess_image(img):
            img = img.convert("L")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(3)
            return img

        img = Image.open("public/uploads/" + img_path)
        processed_img = preprocess_image(img)
        str_img = image_to_string(processed_img, config="--psm 11 --oem 3 tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.:$")
    
    item_pattern = r'(\d+)?\s*([a-zA-Z\s]+)\s*\$?(\d+\.\d{2})'

    # List to hold the items
    items = []

    # Find all matches for the pattern in the str_img text
    matches = re.findall(item_pattern, str_img)

    # Extract item details (no subtotal calculation here)
    for match in matches:
        quantity, item, price = match
        quantity = int(quantity) if quantity else 1  # Default quantity to 1 if not provided
        price = float(price)
        
        # Add to the list
        items.append({
            'item': item.strip(),
            'quantity': quantity,
            'price': price
        })

    # Regular expressions to extract subtotal, tax, and total (allowing missing letters anywhere)
    subtotal_pattern = r'subto?t?a?l\s*\$?(\d+\.\d{2})'  # Handle variations of 'subtotal'
    tax_pattern = r'ta?x\s*\$?(\d+\.\d{2})'  # Handle variations of 'tax'
    tip_pattern = r't?i?p\s*\$?(\d+\.\d{2})' 
    total_pattern = r't?o?t?a?l\s*\$?(\d+\.\d{2})' 
    payment_pattern = r'Payment\s*\$?(\d+\.\d{2})'
    other_pattern = r'Other\s*\$?(\d+\.\d{2})'

    total_matches = re.findall(total_pattern, str_img, re.IGNORECASE)
    payment_match = re.search(payment_pattern, str_img, re.IGNORECASE)

    subtotal_match = re.search(subtotal_pattern, str_img, re.IGNORECASE)
    tax_match = re.search(tax_pattern, str_img, re.IGNORECASE)
    tip_match = re.search(tip_pattern, str_img, re.IGNORECASE)
    other_match = re.search(other_pattern, str_img, re.IGNORECASE)

    # Get the first total (if any)
    total = float(total_matches[0]) if total_matches else None

    # If total equals subtotal, check the next total occurrence
    if total and subtotal_match and float(subtotal_match.group(1)) == total:
        if len(total_matches) > 1:  # Check for a second total
            total = float(total_matches[1])
        else:
            total = None  # If there's no second total, set to None

    # Search for subtotal, tax, and total (with case-insensitivity)
    if payment_match:
        total = float(payment_match.group(1))

    # Extract values if they exist
    subtotal = float(subtotal_match.group(1)) if subtotal_match else None
    tax = float(tax_match.group(1)) if tax_match else None
    tip = float(tip_match.group(1)) if tip_match else None

    if tip is None and other_match:
        tip = float(other_match.group(1))

    # Remove any item where the price equals the total or any variation of subtotal, total, or tax appears in the name
    items = [item for item in items if item['price'] != total and not re.search(r'(total|subtotal|tax)', item['item'], re.IGNORECASE)]

    # Create the final receipt summary
    receipt_summary = {
        'items': items,  # Only items that do not match the total price or contain variations of 'total', 'subtotal', 'tax'
        'subtotal': round(subtotal, 2) if subtotal is not None else None,
        'tax': round(tax, 2) if tax is not None else None,
        'total': round(total, 2) if total is not None else None,
        'tip': round(tip, 2) if tip is not None else None
    }

    # Convert the dictionary to a JSON response (as a string for demonstration)
    json_response = json.dumps(receipt_summary, indent=4)
    return json_response

# ...existing code...