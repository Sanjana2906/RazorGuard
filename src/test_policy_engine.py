import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "test_impact_report.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_policy_decisions.csv"

df = pd.read_csv(INPUT_FILE)


def decide_policy(row):

    exception_type = row["exception_type"]
    severity = row["severity"]
    amount = float(row["amount_at_risk"])

    # High-risk payment/order inconsistencies
    if exception_type == "PAYMENT_ORDER_MISMATCH":
        return "HUMAN_REVIEW"

    # High-value settlement anomalies require review
    if exception_type == "SETTLEMENT_ANOMALY":
        if severity in ["HIGH", "MEDIUM"]:
            return "HUMAN_REVIEW"
        return "AUTO_APPROVE"

    # Refund inconsistencies affect customer liability
    if exception_type == "REFUND_ORDER_MISMATCH":
        return "HUMAN_REVIEW"

    # Webhook failures can be automatically reconciled
    if exception_type == "WEBHOOK_FAILURE":
        if amount < 500:
            return "AUTO_APPROVE"
        return "HUMAN_REVIEW"

    return "HUMAN_REVIEW"


df["decision"] = df.apply(decide_policy, axis=1)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("   RAZORGUARD TEST POLICY ENGINE")
print("===================================\n")

print(f"Exceptions evaluated: {len(df)}")

print("\nDecision breakdown:")
print(df["decision"].value_counts())

print("\nExample:")

columns = [
    "order_id",
    "exception_type",
    "severity",
    "amount_at_risk",
    "decision"
]

print(
    df[columns]
    .head(5)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)