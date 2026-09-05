import pandas as pd

from razorpay_client import build_razorguard_transaction


def detect_live_transaction(order_id):

    transaction = build_razorguard_transaction(order_id)

    # Simulate merchant DB failure:
    # Razorpay says payment is captured,
    # merchant system says order is unpaid.
    transaction["merchant_order_state"] = "unpaid"

    # Fields required by the existing RazorGuard detector
    transaction["settlement_status"] = "NOT_AVAILABLE"
    transaction["settlement_amount"] = 0
    transaction["refund_status"] = "NONE"
    transaction["refund_amount"] = 0
    transaction["webhook_status"] = "NOT_TESTED"

    # Match detector.py's expected uppercase values
    transaction["payment_state"] = transaction["payment_state"].upper()
    transaction["merchant_order_state"] = transaction["merchant_order_state"].upper()

    df = pd.DataFrame([transaction])

    exceptions = []

    for _, row in df.iterrows():

        if (
            row["payment_state"] == "CAPTURED"
            and row["merchant_order_state"] in ["UNPAID", "PENDING"]
        ):
            exceptions.append({
                "order_id": row["order_id"],
                "exception_type": "PAYMENT_ORDER_MISMATCH",
                "severity": "HIGH",
                "amount_affected": abs(float(row["payment_amount"])),
                "reason": "Payment captured but merchant order is not marked as paid"
            })

    print("\n" + "=" * 55)
    print("       RAZORGUARD LIVE DETECTOR")
    print("=" * 55)

    print("\nTransaction:")
    print("Order ID:", transaction["order_id"])
    print("Payment ID:", transaction["payment_id"])
    print("Payment:", transaction["payment_state"])
    print("Merchant Order:", transaction["merchant_order_state"])
    print("Amount: ₹", transaction["payment_amount"])

    if exceptions:
        print("\n🚨 EXCEPTION DETECTED")

        for exception in exceptions:
            print("\nType:", exception["exception_type"])
            print("Severity:", exception["severity"])
            print("Amount at risk: ₹", exception["amount_affected"])
            print("Reason:", exception["reason"])

    else:
        print("\n✓ No exception detected")


if __name__ == "__main__":

    detect_live_transaction(
        "order_TXu8s6quwAZIIW"
    )