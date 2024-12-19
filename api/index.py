from flask import Flask, request, jsonify
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
    username = data.get('username')
    if not session_id or not username or session_id not in sessions:
        emit("error", {"message": "Invalid session or username"})
        return

    join_room(session_id)
    sessions[session_id]['users'][username] = {'claimed_items': [], 'total': 0.0}
    emit("session_update", sessions[session_id], to=session_id)

@socketio.on("claim_item")
def claim_item(data):
    """Allow a user to claim an item."""
    session_id = data.get('session_id')
    username = data.get('username')
    item_name = data.get('item')
    quantity = data.get('quantity', 1)

    if session_id not in sessions or username not in sessions[session_id]['users']:
        emit("error", {"message": "Invalid session or username"})
        return

    session = sessions[session_id]
    user = session['users'][username]

    # Find and update the item
    for item in session['items']:
        if item['item'].lower() == item_name.lower() and item['quantity'] >= quantity:
            item['quantity'] -= quantity
            user['claimed_items'].append({'item': item_name, 'quantity': quantity, 'price': item['price'] * quantity})
            user['total'] += item['price'] * quantity
            break
    else:
        emit("error", {"message": "Item not available or insufficient quantity"})
        return

    emit("session_update", session, to=session_id)

@socketio.on("unclaim_item")
def unclaim_item(data):
    """Allow a user to unclaim an item."""
    session_id = data.get('session_id')
    username = data.get('username')
    item_name = data.get('item')
    quantity = data.get('quantity', 1)

    if session_id not in sessions or username not in sessions[session_id]['users']:
        emit("error", {"message": "Invalid session or username"})
        return

    session = sessions[session_id]
    user = session['users'][username]

    # Find and update the claimed item
    for claimed_item in user['claimed_items']:
        if claimed_item['item'].lower() == item_name.lower() and claimed_item['quantity'] >= quantity:
            claimed_item['quantity'] -= quantity
            user['total'] -= claimed_item['price'] / claimed_item['quantity'] * quantity
            if claimed_item['quantity'] == 0:
                user['claimed_items'].remove(claimed_item)
            break
    else:
        emit("error", {"message": "Item not claimed or insufficient quantity"})
        return

    # Restore the item to the session's receipt
    for item in session['items']:
        if item['item'].lower() == item_name.lower():
            item['quantity'] += quantity
            break

    emit("session_update", session, to=session_id)

# Run the application
if __name__ == "__main__":
    socketio.run(app, debug=True)
