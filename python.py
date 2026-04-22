import os
import argparse
import logging
from binance.client import Client
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# VALIDATORS
# =========================
def validate_side(side):
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")

def validate_order_type(order_type):
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be MARKET or LIMIT")

def validate_quantity(quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")

def validate_price(price, order_type):
    if order_type == "LIMIT" and price is None:
        raise ValueError("Price is required for LIMIT orders")

# =========================
# BINANCE CLIENT
# =========================
def get_client():
    client = Client(API_KEY, API_SECRET)
    client.FUTURES_URL = "https://testnet.binancefuture.com"
    return client

# =========================
# ORDER FUNCTION
# =========================
def place_order(client, symbol, side, order_type, quantity, price=None):
    try:
        logging.info(f"Placing order: {symbol} {side} {order_type} {quantity} {price}")

        if order_type == "MARKET":
            response = client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )

        elif order_type == "LIMIT":
            response = client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )

        logging.info(f"Response: {response}")
        return response

    except Exception as e:
        logging.error(f"Error placing order: {str(e)}")
        raise

# =========================
# MAIN FUNCTION (CLI)
# =========================
def main():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")

    parser.add_argument("--symbol", required=True, help="e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", type=float, required=True)
    parser.add_argument("--price", type=float, help="Required for LIMIT")

    args = parser.parse_args()

    try:
        # VALIDATION
        validate_side(args.side)
        validate_order_type(args.type)
        validate_quantity(args.quantity)
        validate_price(args.price, args.type)

        # INIT CLIENT
        client = get_client()

        # PLACE ORDER
        response = place_order(
            client,
            args.symbol,
            args.side,
            args.type,
            args.quantity,
            args.price
        )

        # OUTPUT
        print("\n✅ ORDER SUCCESS")
        print("===================================")
        print(f"Symbol       : {args.symbol}")
        print(f"Side         : {args.side}")
        print(f"Type         : {args.type}")
        print(f"Quantity     : {args.quantity}")
        print(f"Price        : {args.price if args.price else 'MARKET'}")
        print("===================================")
        print(f"Order ID     : {response.get('orderId')}")
        print(f"Status       : {response.get('status')}")
        print(f"Executed Qty : {response.get('executedQty')}")
        print(f"Avg Price    : {response.get('avgPrice', 'N/A')}")

    except Exception as e:
        print("\n❌ ORDER FAILED")
        print("===================================")
        print(str(e))

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
