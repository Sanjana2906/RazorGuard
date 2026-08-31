import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "test_policy_decisions.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_ai_explanations.csv"

df = pd.read_csv(INPUT_FILE)


def generate_explanation(row):

    exception_type = row["exception_type"]
    amount = float(row["amount_at_risk"])
    decision = row["decision"]

    if exception_type == "PAYMENT_ORDER_MISMATCH":
        explanation = (
            f"The payment was captured, but the merchant order state "
            f"does not match the payment state. ₹{amount:.2f} is potentially "
            f"affected by this inconsistency."
        )
        recommendation = (
            "Reconcile the merchant order with the captured payment "
            "before requesting another payment."
        )

    elif exception_type == "SETTLEMENT_ANOMALY":
        explanation = (
            f"The settlement amount does not fully match the captured "
            f"payment amount, creating a potential financial discrepancy "
            f"of ₹{amount:.2f}."
        )
        recommendation = (
            "Reconcile the settlement against the payment, refunds, "
            "fees and other settlement adjustments."
        )

    elif exception_type == "REFUND_ORDER_MISMATCH":
        explanation = (
            f"The merchant order indicates a refund condition, but the "
            f"corresponding refund has not been completed. "
            f"₹{amount:.2f} may be exposed."
        )
        recommendation = (
            "Verify the refund status and reconcile the merchant order "
            "with the Razorpay refund record."
        )

    elif exception_type == "WEBHOOK_FAILURE":
        explanation = (
            f"A required webhook event failed to reach the merchant "
            f"system. The underlying payment may still be valid, but "
            f"the merchant state may be stale. Amount involved: "
            f"₹{amount:.2f}."
        )
        recommendation = (
            "Verify webhook delivery and replay or reconcile the "
            "missing event."
        )

    else:
        explanation = (
            f"A financial inconsistency involving ₹{amount:.2f} "
            f"was detected."
        )
        recommendation = "Manual investigation required."

    return pd.Series({
        "explanation": explanation,
        "recommendation": recommendation,
        "policy_decision": decision
    })


df[
    ["explanation", "recommendation", "policy_decision"]
] = df.apply(generate_explanation, axis=1)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("   RAZORGUARD TEST AI EXPLAINER")
print("===================================\n")

print(f"Exceptions explained: {len(df)}")

print("\nExample explanation:")

columns = [
    "order_id",
    "exception_type",
    "amount_at_risk",
    "policy_decision",
    "explanation",
    "recommendation"
]

print(
    df[columns]
    .head(1)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)