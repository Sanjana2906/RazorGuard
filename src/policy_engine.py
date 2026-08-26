import pandas as pd
from pathlib import Path

INPUT_FILE = Path("output/impact_report.csv")
OUTPUT_FILE = Path("output/policy_decisions.csv")

df = pd.read_csv(INPUT_FILE)

decisions = []

for _, row in df.iterrows():

    exception_type = row["exception_type"]
    amount = float(row["amount_at_risk"])
    severity = row["severity"]

    # ---------------------------------------------
    # Default decision
    # ---------------------------------------------

    decision = "HUMAN_REVIEW"
    reason = "Financial exception requires human verification."

    # ---------------------------------------------
    # Unknown / unsafe situations
    # ---------------------------------------------

    if exception_type not in [
        "PAYMENT_ORDER_MISMATCH",
        "SETTLEMENT_ANOMALY",
        "REFUND_ORDER_MISMATCH",
        "WEBHOOK_FAILURE"
    ]:

        decision = "BLOCK"
        reason = "Unknown exception type."

    # ---------------------------------------------
    # Webhook failures
    # Non-monetary reconciliation only
    # ---------------------------------------------

    elif exception_type == "WEBHOOK_FAILURE":

        decision = "AUTO_APPROVE"
        reason = (
            "Non-monetary reconciliation action is permitted "
            "for webhook delivery failures."
        )

    # ---------------------------------------------
    # Payment/order mismatch
    # ---------------------------------------------

    elif exception_type == "PAYMENT_ORDER_MISMATCH":

        if amount <= 5000:

            decision = "HUMAN_REVIEW"
            reason = (
                "Payment captured but merchant order is unpaid. "
                "Merchant state must be verified."
            )

        else:

            decision = "HUMAN_REVIEW"
            reason = (
                "High-value payment/order mismatch requires "
                "manual verification."
            )

    # ---------------------------------------------
    # Settlement anomaly
    # ---------------------------------------------

    elif exception_type == "SETTLEMENT_ANOMALY":

        decision = "HUMAN_REVIEW"
        reason = (
            "Settlement discrepancy requires reconciliation "
            "against refunds, fees and adjustments."
        )

    # ---------------------------------------------
    # Refund mismatch
    # ---------------------------------------------

    elif exception_type == "REFUND_ORDER_MISMATCH":

        decision = "HUMAN_REVIEW"
        reason = (
            "Refund status affects customer liability and "
            "requires merchant verification."
        )

    decisions.append({
        "order_id": row["order_id"],
        "exception_type": exception_type,
        "amount_at_risk": amount,
        "severity": severity,
        "decision": decision,
        "reason": reason
    })


decision_df = pd.DataFrame(decisions)

decision_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("        RAZORGUARD POLICY ENGINE")
print("===================================")

print(f"\nExceptions evaluated: {len(decision_df)}")

print("\nDecision breakdown:")
print(
    decision_df["decision"].value_counts()
)

print("\nSaved to:")
print(OUTPUT_FILE)