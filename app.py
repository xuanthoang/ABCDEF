import os
import json
from flask import Flask, request, jsonify, render_template
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv

# Load biến từ .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
WEBHOOK_PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE")

app = Flask(__name__)

client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = 'https://fapi.binance.com'  # Giao dịch Binance Futures

def futures_order(symbol, side, quantity, order_type=FUTURE_ORDER_TYPE_MARKET):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        return order
    except Exception as e:
        print(f"Order error: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    if data.get('passphrase') != WEBHOOK_PASSPHRASE:
        return jsonify({"code": "error", "message": "Invalid passphrase"})

    try:
        side = data['strategy']['order_action'].upper()
        quantity = float(data['strategy']['order_contracts'])
        symbol = data.get('ticker', 'BTCUSDT').upper()

        response = futures_order(symbol, side, quantity)
        if response:
            return jsonify({"code": "success", "message": "Order executed"})
        else:
            return jsonify({"code": "error", "message": "Order failed"})
    except Exception as e:
        return jsonify({"code": "error", "message": str(e)})
