import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "test_detected_exceptions.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_impact_report.csv"

df = pd.read_csv(INPUT_FILE)

print("\n===================================")
print("       RAZORGUARD TEST IMPACT ENGINE")
print("===================================\n")


# --------------------------------------------------
# 1. Calculate amount at risk
# --------------------------------------------------

if "amount_affected" in df.columns:
    df["amount_at_risk"] = df["amount_affected"].abs().round(2)

elif "amount_at_risk" in df.columns:
    df["amount_at_risk"] = df["amount_at_risk"].abs()

else:
    df["amount_at_risk"] = 0.0


# --------------------------------------------------
# 2. Generate evidence
# --------------------------------------------------

def generate_evidence(row):

    exception_type = row.get("exception_type", "")

    if exception_type == "SETTLEMENT_ANOMALY":
        return (
            f"Settlement anomaly detected; "
            f"amount affected=₹{row['amount_at_risk']:.2f}"
        )

    if exception_type == "PAYMENT_ORDER_MISMATCH":
        return (
            f"Payment/order state mismatch; "
            f"amount affected=₹{row['amount_at_risk']:.2f}"
        )

    if exception_type == "REFUND_ORDER_MISMATCH":
        return (
            f"Refund/order state mismatch; "
            f"amount affected=₹{row['amount_at_risk']:.2f}"
        )

    if exception_type == "WEBHOOK_FAILURE":
        return (
            f"Webhook delivery failure; "
            f"amount affected=₹{row['amount_at_risk']:.2f}"
        )

    return (
        f"Financial exception detected; "
        f"amount affected=₹{row['amount_at_risk']:.2f}"
    )


df["evidence"] = df.apply(
    generate_evidence,
    axis=1
)


# --------------------------------------------------
# 3. Determine likely cause
# --------------------------------------------------

def determine_cause(row):

    exception_type = row["exception_type"]

    if exception_type == "PAYMENT_ORDER_MISMATCH":
        return (
            "Payment captured but merchant order state "
            "does not match."
        )

    if exception_type == "SETTLEMENT_ANOMALY":
        return (
            "Settlement amount is lower than the "
            "captured payment amount."
        )

    if exception_type == "REFUND_ORDER_MISMATCH":
        return (
            "Merchant order indicates a refund condition "
            "but the refund is still pending."
        )

    if exception_type == "WEBHOOK_FAILURE":
        return (
            "Required webhook event was not successfully "
            "delivered to the merchant system."
        )

    return "Unknown financial inconsistency."


df["likely_cause"] = df.apply(
    determine_cause,
    axis=1
)


# --------------------------------------------------
# 4. Severity
# --------------------------------------------------

def calculate_severity(row):

    amount = abs(float(row["amount_at_risk"]))

    if amount >= 1000:
        return "HIGH"

    elif amount >= 500:
        return "MEDIUM"

    return "LOW"


df["severity"] = df.apply(
    calculate_severity,
    axis=1
)


# --------------------------------------------------
# 5. Recommended action
# --------------------------------------------------

def recommend_action(row):

    exception_type = row["exception_type"]

    if exception_type == "PAYMENT_ORDER_MISMATCH":
        return (
            "Reconcile the merchant order state with "
            "the captured payment before requesting "
            "another payment."
        )

    if exception_type == "SETTLEMENT_ANOMALY":
        return (
            "Reconcile the settlement against payment, "
            "refunds, fees and other settlement adjustments."
        )

    if exception_type == "REFUND_ORDER_MISMATCH":
        return (
            "Verify refund status and reconcile the "
            "merchant order with the refund record."
        )

    if exception_type == "WEBHOOK_FAILURE":
        return (
            "Verify webhook delivery and replay or "
            "reconcile the missing event."
        )

    return "Manual investigation required."


df["recommended_action"] = df.apply(
    recommend_action,
    axis=1
)


# --------------------------------------------------
# 6. Save test impact report
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print(
    f"Exceptions with evidence: {len(df)}"
)

print(
    f"\nTotal amount affected: "
    f"₹{df['amount_at_risk'].sum():.2f}"
)

print("\nBy exception type:")
print(
    df["exception_type"].value_counts()
)

print("\nExample:")

columns_to_show = [
    "order_id",
    "exception_type",
    "severity",
    "amount_at_risk",
    "evidence",
    "likely_cause",
    "recommended_action"
]

print(
    df[columns_to_show]
    .head(1)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)

