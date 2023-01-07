import json, config, requests, time, hashlib, hmac, urllib.request, urllib.parse
from flask import Flask, request, jsonify, render_template
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

client = Client(config.API_KEY, config.API_SECRET, tld='us')
clientTestNet = Client(config.API_KEY_TEST, config.API_SECRET_TEST, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        # order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        url = "https://testnet.binance.vision/api/v3/order"
        headers = {"Content-Type":"application/json", "X-MBX-APIKEY":config.API_KEY_TEST}
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": int(time.time() * 1000)
        }

        secret = bytes(config.API_SECRET_TEST.encode('utf-8'))
        signature = hmac.new(secret, urllib.parse.urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()

        params['signature'] = signature

        order = requests.post(url= url, headers= headers, params= params)

        print(order.content)

    except Exception as e:
        print("an exception occurred - {}".format(e))
        return False

    return order

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    #print(request.data)
    data = json.loads(request.data)
    
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    order_response = order(side, quantity, "BTCUSDT")

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")

        return {
            "code": "error",
            "message": "order failed"
        }