
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "razorguard_test.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_financial_states.csv"

df = pd.read_csv(INPUT_FILE)

states = []

for _, row in df.iterrows():

    payment_state = row["payment_state"]
    merchant_state = row["merchant_order_state"]
    settlement_state = row["settlement_status"]
    refund_state = row["refund_status"]
    webhook_status = row["webhook_status"]

    # ---------------------------------------------
    # Determine overall financial state
    # ---------------------------------------------

    # Webhook failure must be checked first
    if (
        payment_state == "CAPTURED"
        and webhook_status == "FAILED"
    ):
        overall_state = "WEBHOOK_EXCEPTION"

    elif (
        payment_state == "CAPTURED"
        and merchant_state == "UNPAID"
    ):
        overall_state = "PAYMENT_CAPTURED_ORDER_UNPAID"

    elif (
        settlement_state == "PARTIAL"
    ):
        overall_state = "SETTLEMENT_EXCEPTION"

    elif (
        merchant_state == "CANCELLED"
        and refund_state == "PENDING"
    ):
        overall_state = "REFUND_PENDING"

    elif (
        payment_state == "CAPTURED"
        and merchant_state == "PAID"
        and settlement_state == "SETTLED"
        and refund_state == "NOT_REFUNDED"
        and webhook_status == "DELIVERED"
    ):
        overall_state = "CONSISTENT"

    else:
        overall_state = "REVIEW_REQUIRED"

    # ---------------------------------------------
    # Calculate financial exposure
    # ---------------------------------------------

    if overall_state == "SETTLEMENT_EXCEPTION":

        financial_exposure = max(
            0,
            row["payment_amount"] - row["settlement_amount"]
        )

    elif overall_state == "REFUND_PENDING":

        financial_exposure = row["refund_amount"]

    elif overall_state == "PAYMENT_CAPTURED_ORDER_UNPAID":

        financial_exposure = row["payment_amount"]

    elif overall_state == "WEBHOOK_EXCEPTION":

        financial_exposure = row["payment_amount"]

    else:

        financial_exposure = 0.0

    states.append({
        "order_id": row["order_id"],
        "payment_state": payment_state,
        "merchant_order_state": merchant_state,
        "settlement_state": settlement_state,
        "refund_state": refund_state,
        "webhook_status": webhook_status,
        "overall_state": overall_state,
        "financial_exposure": round(
            financial_exposure,
            2
        )
    })


states_df = pd.DataFrame(states)

states_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("       RAZORGUARD TEST STATE MACHINE")
print("===================================")

print(
    f"\nTransactions processed: {len(states_df)}"
)

print("\nState distribution:")

print(
    states_df["overall_state"]
    .value_counts()
)

print(
    "\nTotal financial exposure: ₹"
    + str(
        round(
            states_df["financial_exposure"].sum(),
            2
        )
    )
)

print("\nSaved to:")
print(OUTPUT_FILE)