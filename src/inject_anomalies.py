import pandas as pd
import random
from pathlib import Path

INPUT_FILE = Path("output/razorguard_base.csv")
OUTPUT_FILE = Path("output/razorguard_test.csv")
GROUND_TRUTH_FILE = Path("output/ground_truth.csv")

random.seed(42)

df = pd.read_csv(INPUT_FILE)

# Track injected anomalies
ground_truth = []

# ---------------------------------------------------------
# Select 50 UNIQUE records
# ---------------------------------------------------------

available = list(df.index)
random.shuffle(available)

payment_order_indices = available[:20]
settlement_indices = available[20:35]
refund_indices = available[35:45]
webhook_indices = available[45:50]


# ---------------------------------------------------------
# 1. PAYMENT ↔ ORDER MISMATCH
# ---------------------------------------------------------

for idx in payment_order_indices:

    df.loc[idx, "payment_state"] = "CAPTURED"
    df.loc[idx, "merchant_order_state"] = "UNPAID"

    ground_truth.append({
        "index": idx,
        "order_id": df.loc[idx, "order_id"],
        "anomaly_type": "PAYMENT_ORDER_MISMATCH",
        "expected_detection": True
    })


# ---------------------------------------------------------
# 2. SETTLEMENT ANOMALY
# ---------------------------------------------------------

for idx in settlement_indices:

    payment_amount = df.loc[idx, "payment_amount"]

    # Make settlement 30% lower
    settlement_amount = round(payment_amount * 0.70, 2)

    df.loc[idx, "settlement_amount"] = settlement_amount
    df.loc[idx, "settlement_status"] = "PARTIAL"

    ground_truth.append({
        "index": idx,
        "order_id": df.loc[idx, "order_id"],
        "anomaly_type": "SETTLEMENT_ANOMALY",
        "expected_detection": True
    })


# ---------------------------------------------------------
# 3. REFUND ↔ ORDER MISMATCH
# ---------------------------------------------------------

for idx in refund_indices:

    payment_amount = df.loc[idx, "payment_amount"]

    df.loc[idx, "merchant_order_state"] = "CANCELLED"
    df.loc[idx, "refund_status"] = "PENDING"
    df.loc[idx, "refund_amount"] = round(payment_amount, 2)

    ground_truth.append({
        "index": idx,
        "order_id": df.loc[idx, "order_id"],
        "anomaly_type": "REFUND_ORDER_MISMATCH",
        "expected_detection": True
    })


# ---------------------------------------------------------
# 4. WEBHOOK FAILURE
# ---------------------------------------------------------

for idx in webhook_indices:

    df.loc[idx, "payment_state"] = "CAPTURED"
    df.loc[idx, "webhook_status"] = "FAILED"

    ground_truth.append({
        "index": idx,
        "order_id": df.loc[idx, "order_id"],
        "anomaly_type": "WEBHOOK_FAILURE",
        "expected_detection": True
    })


# ---------------------------------------------------------
# Save test dataset
# ---------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

truth_df = pd.DataFrame(ground_truth)

truth_df.to_csv(
    GROUND_TRUTH_FILE,
    index=False
)

print("Anomaly injection complete!")

print("\nDataset:")
print(f"Total records: {len(df)}")

print("\nInjected anomalies:")
print(truth_df["anomaly_type"].value_counts())

print("\nGround truth:")
print(GROUND_TRUTH_FILE)

print("\nTest dataset:")
print(OUTPUT_FILE)