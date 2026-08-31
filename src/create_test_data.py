import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "razorguard_base.csv"
OUTPUT_FILE = BASE_DIR / "output" / "razorguard_test.csv"
GROUND_TRUTH_FILE = BASE_DIR / "output" / "test_ground_truth.csv"

np.random.seed(42)

df = pd.read_csv(INPUT_FILE)

# Take a different 500-record sample
test_df = df.sample(
    n=min(500, len(df)),
    random_state=123
).copy()

# Reset any previous anomaly-related fields
test_df["ground_truth_exception"] = "NONE"

# Select deterministic anomaly indices
indices = test_df.index.tolist()

payment_mismatch_idx = indices[:20]
settlement_idx = indices[20:35]
refund_idx = indices[35:45]
webhook_idx = indices[45:50]

# --------------------------------------------------
# 1. Payment ↔ Order mismatch
# --------------------------------------------------

test_df.loc[
    payment_mismatch_idx,
    "merchant_order_state"
] = "UNPAID"

test_df.loc[
    payment_mismatch_idx,
    "payment_state"
] = "CAPTURED"

test_df.loc[
    payment_mismatch_idx,
    "ground_truth_exception"
] = "PAYMENT_ORDER_MISMATCH"


# --------------------------------------------------
# 2. Settlement anomaly
# --------------------------------------------------

test_df.loc[
    settlement_idx,
    "settlement_status"
] = "PARTIAL"

test_df.loc[
    settlement_idx,
    "settlement_amount"
] = (
    test_df.loc[
        settlement_idx,
        "payment_amount"
    ] * 0.70
)

test_df.loc[
    settlement_idx,
    "ground_truth_exception"
] = "SETTLEMENT_ANOMALY"


# --------------------------------------------------
# 3. Refund ↔ Order mismatch
# --------------------------------------------------

test_df.loc[
    refund_idx,
    "merchant_order_state"
] = "CANCELLED"

test_df.loc[
    refund_idx,
    "refund_status"
] = "PENDING"

test_df.loc[
    refund_idx,
    "refund_amount"
] = test_df.loc[
    refund_idx,
    "payment_amount"
]

test_df.loc[
    refund_idx,
    "ground_truth_exception"
] = "REFUND_ORDER_MISMATCH"


# --------------------------------------------------
# 4. Webhook failure
# --------------------------------------------------

test_df.loc[
    webhook_idx,
    "webhook_status"
] = "FAILED"

test_df.loc[
    webhook_idx,
    "ground_truth_exception"
] = "WEBHOOK_FAILURE"


# --------------------------------------------------
# Calculate expected financial difference
# --------------------------------------------------

test_df["amount_difference"] = (
    test_df["expected_amount"]
    - test_df["payment_amount"]
).abs()

# Save ground truth separately
ground_truth = test_df[
    ["order_id", "ground_truth_exception"]
].copy()

ground_truth.to_csv(
    GROUND_TRUTH_FILE,
    index=False
)

# IMPORTANT:
# Detector must not receive the ground-truth column.
detector_input = test_df.drop(
    columns=["ground_truth_exception"]
)

detector_input.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("     HELD-OUT TEST DATA")
print("===================================\n")

print(
    f"Test transactions: {len(detector_input)}"
)

print("\nHidden anomalies:")
print(
    ground_truth[
        ground_truth["ground_truth_exception"] != "NONE"
    ]["ground_truth_exception"].value_counts()
)

print("\nSaved:")
print(OUTPUT_FILE)

print("\nGround truth saved separately:")
print(GROUND_TRUTH_FILE)