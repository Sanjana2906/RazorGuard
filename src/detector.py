import pandas as pd
from pathlib import Path

INPUT_FILE = Path("output/razorguard_test.csv")
OUTPUT_FILE = Path("output/detected_exceptions.csv")

df = pd.read_csv(INPUT_FILE)

exceptions = []

for _, row in df.iterrows():

    # -----------------------------------------------------
    # 1. Payment ↔ Merchant Order mismatch
    # -----------------------------------------------------
    if (
        row["payment_state"] == "CAPTURED"
        and row["merchant_order_state"] == "UNPAID"
    ):
        exceptions.append({
            "order_id": row["order_id"],
            "exception_type": "PAYMENT_ORDER_MISMATCH",
            "severity": "HIGH",
            "amount_affected": row["payment_amount"],
            "reason": (
                "Payment is captured but merchant order "
                "is still marked UNPAID"
            )
        })

    # -----------------------------------------------------
    # 2. Settlement anomaly
    # -----------------------------------------------------
    elif row["settlement_status"] == "PARTIAL":

        difference = (
            row["payment_amount"] -
            row["settlement_amount"]
        )

        exceptions.append({
            "order_id": row["order_id"],
            "exception_type": "SETTLEMENT_ANOMALY",
            "severity": "HIGH",
            "amount_affected": round(difference, 2),
            "reason": (
                "Settlement amount is lower than "
                "the captured payment amount"
            )
        })

    # -----------------------------------------------------
    # 3. Refund ↔ Order mismatch
    # -----------------------------------------------------
    elif (
        row["merchant_order_state"] == "CANCELLED"
        and row["refund_status"] == "PENDING"
    ):
        exceptions.append({
            "order_id": row["order_id"],
            "exception_type": "REFUND_ORDER_MISMATCH",
            "severity": "MEDIUM",
            "amount_affected": row["refund_amount"],
            "reason": (
                "Merchant order is cancelled but "
                "customer refund is still pending"
            )
        })

    # -----------------------------------------------------
    # 4. Webhook failure
    # -----------------------------------------------------
    elif (
        row["payment_state"] == "CAPTURED"
        and row["webhook_status"] == "FAILED"
    ):
        exceptions.append({
            "order_id": row["order_id"],
            "exception_type": "WEBHOOK_FAILURE",
            "severity": "HIGH",
            "amount_affected": row["payment_amount"],
            "reason": (
                "Payment is captured but the "
                "webhook delivery failed"
            )
        })


# ---------------------------------------------------------
# Save detected exceptions
# ---------------------------------------------------------

exceptions_df = pd.DataFrame(exceptions)

exceptions_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("       RAZORGUARD DETECTOR")
print("===================================")

print(f"\nTransactions analyzed: {len(df)}")
print(f"Exceptions detected: {len(exceptions_df)}")

if len(exceptions_df) > 0:

    print("\nException breakdown:")
    print(
        exceptions_df["exception_type"]
        .value_counts()
    )

    print("\nTotal affected amount: ₹",
          round(
              exceptions_df["amount_affected"].sum(),
              2
          ))

print("\nSaved to:")
print(OUTPUT_FILE)