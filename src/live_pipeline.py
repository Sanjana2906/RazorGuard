import pandas as pd

from razorpay_client import build_razorguard_transaction


def run_live_detection(order_id):

    print("\n" + "=" * 60)
    print("       RAZORGUARD LIVE PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # 1. FETCH LIVE RAZORPAY DATA
    # --------------------------------------------------

    transaction = build_razorguard_transaction(order_id)

    # --------------------------------------------------
    # 2. SIMULATE MERCHANT-SIDE STATE
    # --------------------------------------------------
    # Razorpay says payment is captured.
    # Merchant database incorrectly says unpaid.
    #
    # This is the cross-system inconsistency
    # RazorGuard is designed to detect.

    transaction["merchant_order_state"] = "UNPAID"

    # --------------------------------------------------
    # 3. COMPLETE RAZORGUARD SCHEMA
    # --------------------------------------------------

    transaction["settlement_status"] = "NOT_AVAILABLE"
    transaction["settlement_amount"] = 0

    transaction["refund_status"] = "NONE"
    transaction["refund_amount"] = 0

    transaction["webhook_status"] = "RECEIVED"

    transaction["payment_state"] = (
        transaction["payment_state"].upper()
    )

    transaction["merchant_order_state"] = (
        transaction["merchant_order_state"].upper()
    )

    df = pd.DataFrame([transaction])

    # --------------------------------------------------
    # 4. RUN SAME LOGIC AS DETECTOR
    # --------------------------------------------------

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
                "amount_affected": abs(
                    float(row["payment_amount"])
                ),
                "reason":
                    "Payment captured but merchant order "
                    "is not marked as paid"
            })

    # --------------------------------------------------
    # 5. DISPLAY RESULT
    # --------------------------------------------------

    print("\nLIVE TRANSACTION")
    print("-" * 30)

    print("Order ID:",
          transaction["order_id"])

    print("Payment ID:",
          transaction["payment_id"])

    print("Payment State:",
          transaction["payment_state"])

    print("Merchant State:",
          transaction["merchant_order_state"])

    print("Amount: ₹",
          transaction["payment_amount"])

    if exceptions:

        exception = exceptions[0]

        print("\n🚨 RAZORGUARD EXCEPTION")
        print("-" * 30)

        print("Type:",
              exception["exception_type"])

        print("Severity:",
              exception["severity"])

        print(
            "Amount at risk: ₹",
            exception["amount_affected"]
        )

        print("Reason:",
              exception["reason"])

    else:

        print("\n✓ No exception detected")

    return transaction, exceptions


if __name__ == "__main__":

    # Replace with a Razorpay Test Mode order ID
    # that has a captured payment.

    ORDER_ID = "order_TXvgHrM484ESVw"

    run_live_detection(ORDER_ID)