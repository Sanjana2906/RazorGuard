import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "razorguard_test.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_detected_exceptions.csv"

df = pd.read_csv(INPUT_FILE)

exceptions = []


def add_exception(row, exception_type, severity, amount, reason):
    exceptions.append({
        "order_id": row["order_id"],
        "exception_type": exception_type,
        "severity": severity,
        "amount_affected": abs(float(amount)),
        "reason": reason
    })


for _, row in df.iterrows():

    # --------------------------------------------------
    # 1. PAYMENT ↔ ORDER MISMATCH
    # --------------------------------------------------

    if (
        row["payment_state"] == "CAPTURED"
        and row["merchant_order_state"] in ["UNPAID", "PENDING"]
    ):
        add_exception(
            row,
            "PAYMENT_ORDER_MISMATCH",
            "HIGH",
            row["payment_amount"],
            "Payment captured but merchant order is not marked as paid"
        )

    # --------------------------------------------------
    # 2. SETTLEMENT ANOMALY
    # --------------------------------------------------

    elif (
        row["settlement_status"] == "PARTIAL"
        and row["settlement_amount"] < row["payment_amount"]
    ):
        amount = (
            row["payment_amount"]
            - row["settlement_amount"]
        )

        add_exception(
            row,
            "SETTLEMENT_ANOMALY",
            "HIGH",
            amount,
            "Settlement amount is lower than the captured payment amount"
        )

    # --------------------------------------------------
    # 3. REFUND ↔ ORDER MISMATCH
    # --------------------------------------------------

    elif (
        row["merchant_order_state"] == "CANCELLED"
        and row["refund_status"] == "PENDING"
    ):
        add_exception(
            row,
            "REFUND_ORDER_MISMATCH",
            "MEDIUM",
            row["refund_amount"],
            "Merchant order is cancelled but customer refund is still pending"
        )

    # --------------------------------------------------
    # 4. WEBHOOK FAILURE
    # --------------------------------------------------

    elif row["webhook_status"] == "FAILED":

        add_exception(
            row,
            "WEBHOOK_FAILURE",
            "MEDIUM",
            row["payment_amount"],
            "Webhook delivery failed for the transaction"
        )


exceptions_df = pd.DataFrame(exceptions)

if exceptions_df.empty:
    exceptions_df = pd.DataFrame(
        columns=[
            "order_id",
            "exception_type",
            "severity",
            "amount_affected",
            "reason"
        ]
    )


exceptions_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n===================================")
print("       RAZORGUARD TEST DETECTOR")
print("===================================\n")

print(
    f"Transactions analyzed: {len(df)}"
)

print(
    f"Exceptions detected: {len(exceptions_df)}"
)

if not exceptions_df.empty:

    print("\nException breakdown:")

    print(
        exceptions_df["exception_type"]
        .value_counts()
    )

    print(
        f"\nTotal affected amount: "
        f"₹{exceptions_df['amount_affected'].sum():.2f}"
    )

print("\nSaved to:")
print(OUTPUT_FILE)