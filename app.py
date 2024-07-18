from flask import Flask, request, jsonify
import uuid
import math
from datetime import datetime

app = Flask(__name__)

receipts = {}

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    receipt = request.json
    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = receipt
    return jsonify({"id": receipt_id})

@app.route('/receipts/<id>/points', methods=['GET'])
def get_points(id):
    receipt = receipts.get(id)
    if receipt is None:
        return jsonify({"error": "Receipt not found"}), 404
    
    points = calculate_points(receipt)
    return jsonify({"points": points})

def calculate_points(receipt):
    points = 0
    
    # Rule 1: One point for every alphanumeric character in the retailer name
    retailer = receipt.get("retailer", "")
    points += sum(1 for char in retailer if char.isalnum())
    
    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = float(receipt.get("total", "0"))
    if total.is_integer():
        points += 50
    
    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25
    
    # Rule 4: 5 points for every two items on the receipt
    items = receipt.get("items", [])
    points += (len(items) // 2) * 5
    
    # Rule 5: If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer
    for item in items:
        description = item.get("shortDescription", "").strip()
        if len(description) % 3 == 0:
            price = float(item.get("price", "0"))
            points += math.ceil(price * 0.2)
    
    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.get("purchaseDate", ""), "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6
    
    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.get("purchaseTime", ""), "%H:%M")
    if 14 <= purchase_time.hour < 16:
        points += 10
    
    return points

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)