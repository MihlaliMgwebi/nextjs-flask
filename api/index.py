from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageFilter, ImageEnhance
from pytesseract import image_to_string
from PIL import Image
import fitz
import io
import re
import json
import numpy as np
from flask_socketio import SocketIO, join_room, leave_room, emit
from uuid import uuid4
app = Flask(__name__)
#CORS(app)

# ...existing code...

@app.route("/api/processbill")
def process_bill():
    if request.method == "GET":
        #img_path = request.url.split("?image=")[1]

        def preprocess_image(img):
            img = img.convert("L")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(3)
            return img

        img = Image.open(io.BytesIO(request.data))
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




socketio = SocketIO(app, cors_allowed_origins="*")

# Store session data
sessions = {}

@app.route("/api/create_session", methods=["POST"])
def create_session():
    """Create a new session for the bill."""
    try:
        # Parse the bill data
        bill_data = request.json
        session_id = str(uuid4())  # Unique session ID
        sessions[session_id] = {
            "bill": bill_data,
            "users": {}
        }
        return jsonify({"session_id": session_id, "link": f"http://127.0.0.1:5000/session/{session_id}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@socketio.on("join_session")
def join_session(data):
    """Allow a user to join a session."""
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    
    if session_id not in sessions:
        emit("error", {"message": "Invalid session ID"})
        return
    
    join_room(session_id)
    sessions[session_id]["users"][user_id] = {"claimed_items": [], "total": 0}
    emit("session_joined", {"message": f"User {user_id} joined session {session_id}"}, room=session_id)
    emit("bill_update", sessions[session_id]["bill"], room=session_id)

@socketio.on("claim_item")
def claim_item(data):
    """Handle claiming an item from the bill."""
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    item_name = data.get("item_name")
    claim_quantity = data.get("quantity")
    
    if session_id not in sessions or user_id not in sessions[session_id]["users"]:
        emit("error", {"message": "Invalid session or user ID"})
        return

    # Get the bill and user's data
    bill = sessions[session_id]["bill"]
    user_data = sessions[session_id]["users"][user_id]
    
    # Find the item in the bill
    for item in bill["items"]:
        if item["item"].lower() == item_name.lower():
            if item["quantity"] >= claim_quantity:
                item["quantity"] -= claim_quantity
                claimed_total = claim_quantity * item["price"]
                user_data["claimed_items"].append({
                    "item": item["item"],
                    "quantity": claim_quantity,
                    "price": item["price"]
                })
                user_data["total"] += claimed_total
                bill["total"] -= claimed_total
                
                # Broadcast updates to all users
                emit("bill_update", bill, room=session_id)
                emit("user_update", user_data, to=request.sid)
                return
            else:
                emit("error", {"message": "Not enough quantity available"})
                return
    
    emit("error", {"message": "Item not found in bill"})

@socketio.on("leave_session")
def leave_session(data):
    """Handle a user leaving the session."""
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    
    if session_id in sessions and user_id in sessions[session_id]["users"]:
        leave_room(session_id)
        del sessions[session_id]["users"][user_id]
        emit("user_left", {"message": f"User {user_id} left session {session_id}"}, room=session_id)
    else:
        emit("error", {"message": "Invalid session or user ID"})

if __name__ == "__main__":
    socketio.run(app, debug=True)
