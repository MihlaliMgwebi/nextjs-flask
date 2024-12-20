from flask import Flask, redirect, request, jsonify, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit
from PIL import Image, ImageEnhance, UnidentifiedImageError
import pytesseract
import io
import re
import json
from uuid import uuid4

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Store session data
sessions = {}
@app.route("/api/processbill", methods=["POST"])
def process_bill():
    if request.method == "POST":
        try:
            # Check if the content type is correct
            if 'multipart/form-data' not in request.content_type:
                return jsonify({"error": "Invalid content type"}), 400

            # Get the file from the request
            file = request.files.get('file')
            if not file:
                return jsonify({"error": "No file provided"}), 400

            # Process the image
            img = Image.open(file.stream)
            def preprocess_image(img):
                img = img.convert("L")
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(3)
                return img

            processed_img = preprocess_image(img)
            str_img = pytesseract.image_to_string(processed_img, config="--psm 11 --oem 3 tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.:$")
        
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

            # Create a new session for the bill
            session_id = str(uuid4())  # Unique session ID
            user_id = str(uuid4())  # Unique user ID
            sessions[session_id] = {
                "receipt_summary": receipt_summary,
                "users": {
                    user_id: {
                        "claimed_items": [],
                        "total": 0
                    }
                }
            }

            # Convert the dictionary to a JSON response
            return jsonify({"session_id": session_id, "user_id": user_id,"link": "/session/{}".format(session_id), "receipt_summary": receipt_summary})
        except UnidentifiedImageError:
            return jsonify({"error": "Cannot identify image file"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# ...existing code...
    """Process the uploaded receipt and create a session."""
    try:
        # Check for file in request
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Process the image
        img = Image.open(file.stream)
        def preprocess_image(img):
            img = img.convert("L")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(3)
            return img

        processed_img = preprocess_image(img)
        str_img = pytesseract.image_to_string(processed_img, config="--psm 11 --oem 3 tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.:$")

        # Extract receipt data (items, totals, etc.)
        item_pattern = r'(\d+)?\s*([a-zA-Z\s]+)\s*\$?(\d+\.\d{2})'
        items = []
        matches = re.findall(item_pattern, str_img)
        for match in matches:
            quantity, item, price = match
            quantity = int(quantity) if quantity else 1
            price = float(price)
            items.append({
                'item': item.strip(),
                'quantity': quantity,
                'price': price
            })

        # Extract totals and tip
        subtotal_pattern = r'subto?t?a?l\s*\$?(\d+\.\d{2})'
        total_pattern = r't?o?t?a?l\s*\$?(\d+\.\d{2})'
        tip_pattern = r't?i?p\s*\$?(\d+\.\d{2})'

        subtotal_match = re.search(subtotal_pattern, str_img, re.IGNORECASE)
        total_match = re.search(total_pattern, str_img, re.IGNORECASE)
        tip_match = re.search(tip_pattern, str_img, re.IGNORECASE)

        subtotal = float(subtotal_match.group(1)) if subtotal_match else None
        total = float(total_match.group(1)) if total_match else None
        tip = float(tip_match.group(1)) if tip_match else None

        # Create a new session
        session_id = str(uuid4())
        sessions[session_id] = {
            'host': request.remote_addr,
            'items': items,
            'subtotal': subtotal,
            'total': total,
            'tip': tip,
            'users': {}
        }

        return jsonify({"session_id": session_id, "link": "/session/{}".format(session_id), "receipt": sessions[session_id]})


    except UnidentifiedImageError:
        return jsonify({"error": "Cannot identify image file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on("join_session")
def join_session(data):
    """Allow a user to join a session."""
    session_id = data.get('session_id')
    user_id = data.get('user_id') or str(uuid4())

    if not session_id or not user_id or session_id not in sessions:
        emit("error", {"message": "Invalid session or user_id"})
        return

    join_room(session_id)
    sessions[session_id]['users'][user_id] = {'claimed_items': [], 'total': 0.0}
    
    session_update_data = {
        "receipt_summary": sessions[session_id]['receipt_summary'],
        "users": sessions[session_id]['users'],
        "session_id": session_id,
        "user_id": user_id
    }
    emit("session_update", session_update_data, to=session_id)
    return jsonify({"session_id": session_id, "link": "/session/{}".format(session_id), "receipt": sessions[session_id]})
  

@socketio.on("claim_item")
def claim_item(data):
    """Allow a user to claim an item."""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    item_data = data.get('item')
    item_name = item_data.get('item')
    quantity = item_data.get('quantity', 1)

    if session_id not in sessions or user_id not in sessions[session_id]['users']:
        emit("error", {"message": "Invalid session or user_id"})
        return

    session = sessions[session_id]
    user = session['users'][user_id]
    receipt_summary = session['receipt_summary']

    # Find and update the item
    for item in receipt_summary['items']:
        if item['item'].lower() == item_name.lower() and item['quantity'] >= quantity:
            item['quantity'] -= quantity
            user['claimed_items'].append({'item': item_name, 'quantity': quantity, 'price': item['price'] * quantity})
            user['total'] += item['price'] * quantity
            receipt_summary['total'] -= item['price'] * quantity
            if item['quantity'] == 0:
                receipt_summary['items'].remove(item)
            break
    else:
        emit("error", {"message": "Item not available or insufficient quantity"})
        return
    
    # Emit the updated session data
    emit("session_update", {
        "receipt_summary": receipt_summary,
        "users": session['users'],
        "session_id": session_id,
        "user_id": user_id
    }, to=session_id)

@socketio.on("unclaim_item")
def unclaim_item(data):
    """Allow a user to unclaim an item."""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    item_data = data.get('item')
    item_name = item_data.get('item')
    quantity = item_data.get('quantity', 1)

    if session_id not in sessions or user_id not in sessions[session_id]['users']:
        emit("error", {"message": "Invalid session or user_id"})
        return

    session = sessions[session_id]
    user = session['users'][user_id]
    receipt_summary = session['receipt_summary']

    # Find and update the claimed item
    for claimed_item in user['claimed_items']:
        if claimed_item['item'].lower() == item_name.lower() and claimed_item['quantity'] >= quantity:
            price_per_unit = claimed_item['price'] / claimed_item['quantity'] if claimed_item['quantity'] > 0 else 0
            claimed_item['quantity'] -= quantity
            user['total'] -= price_per_unit * quantity
            receipt_summary['total'] += price_per_unit * quantity
            if claimed_item['quantity'] == 0:
                user['claimed_items'].remove(claimed_item)
            break
    else:
        emit("error", {"message": "Item not claimed or insufficient quantity"})
        return

    # Restore the item to the session's receipt
    for item in receipt_summary['items']:
        if item['item'].lower() == item_name.lower():
            item['quantity'] += quantity
            break
    else:
        receipt_summary['items'].append({'item': item_name, 'quantity': quantity, 'price': price_per_unit * quantity})

    # Emit the updated session data
    emit("session_update", {
        "receipt_summary": receipt_summary,
        "users": session['users'],
        "session_id": session_id,
        "user_id": user_id
    }, to=session_id)

# Run the application
if __name__ == "__main__":
    socketio.run(app, debug=False, port=5328)
