import os
import razorpay
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not KEY_ID or not KEY_SECRET:
    raise ValueError(
        "Missing Razorpay credentials. "
        "Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env"
    )

# Create Razorpay client
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))


def fetch_orders(count=10):
    """Fetch orders from Razorpay Test Mode."""
    return client.order.all({
        "count": count
    })


def fetch_payments(count=10):
    """Fetch payments from Razorpay Test Mode."""
    return client.payment.all({
        "count": count
    })

def create_test_order(amount_rupees=100):
    """Create a Razorpay Test Mode order."""
    amount_paise = int(amount_rupees * 100)

    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": "razorguard_demo_001",
        "notes": {
            "project": "RazorGuard",
            "purpose": "Buildathon demo"
        }
    })

    return order

def get_order_with_payments(order_id):
    """Fetch a Razorpay order and all payments linked to it."""
    order = fetch_order(order_id)
    payments = fetch_order_payments(order_id)

    return {
        "order": order,
        "payments": payments.get("items", [])
    }

def simulate_merchant_state(transaction):
    """
    Simulate a merchant-side database failure.
    Razorpay payment remains genuine; only the merchant state is wrong.
    """
    transaction["merchant_order_state"] = "unpaid"
    return transaction

def build_razorguard_transaction(order_id):
    """
    Convert a Razorpay Order + Payment into the normalized
    structure RazorGuard can reason about.
    """
    data = get_order_with_payments(order_id)

    order = data["order"]
    payments = data["payments"]

    # Prefer a captured payment because RazorGuard
# should evaluate the successfully completed transaction.
    payment = next(
        (p for p in payments if p.get("status") == "captured"),
        payments[0] if payments else None
    )

    return {
        "order_id": order["id"],
        "payment_id": payment["id"] if payment else None,

        # Amounts in rupees
        "expected_amount": order["amount"] / 100,
        "payment_amount": payment["amount"] / 100 if payment else 0,

        # Razorpay states
        "merchant_order_state": order["status"],
        "payment_state": payment["status"] if payment else "not_paid",

        # Basic consistency checks
        "amount_difference": (
            (payment["amount"] - order["amount"]) / 100
            if payment else -order["amount"] / 100
        ),

        "amount_match": (
            payment is not None
            and payment["amount"] == order["amount"]
        )
    }

def fetch_order(order_id):
    """Fetch a specific Razorpay order."""
    return client.order.fetch(order_id)

def fetch_order_payments(order_id):
    """Fetch payments associated with a Razorpay order."""
    return client.order.payments(order_id)

if __name__ == "__main__":
    print("=" * 55)
    print("       RAZORGUARD LIVE TRANSACTION")
    print("=" * 55)

    try:
        order_id = "order_TXu8s6quwAZIIW"

        transaction = build_razorguard_transaction(order_id)
        transaction = simulate_merchant_state(transaction)
        print("\nNORMALIZED TRANSACTION")
        print("-" * 30)

        for key, value in transaction.items():
            print(f"{key}: {value}")

        print("\nRAZORGUARD CHECK")
        print("-" * 30)

        if transaction["amount_match"]:
            print("✓ PAYMENT/ORDER AMOUNT CONSISTENT")
        else:
            print("🚨 PAYMENT/ORDER AMOUNT MISMATCH")

        if transaction["merchant_order_state"] == "paid":
            print("✓ MERCHANT ORDER STATE: PAID")
        else:
            print("🚨 MERCHANT ORDER STATE:", 
                  transaction["merchant_order_state"])

        if transaction["payment_state"] == "captured":
            print("✓ PAYMENT STATE: CAPTURED")
        else:
            print("🚨 PAYMENT STATE:",
                  transaction["payment_state"])

    except Exception as e:
        print("\nFAILED")
        print("Error:", e)