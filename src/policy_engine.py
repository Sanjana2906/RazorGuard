import pandas as pd
from pathlib import Path


INPUT_FILE = Path("output/impact_report.csv")
OUTPUT_FILE = Path("output/policy_decisions.csv")


def evaluate_policy(row):
    """
    Evaluate one RazorGuard financial exception
    and return a bounded policy decision.
    """

    exception_type = row["exception_type"]
    amount = float(row["amount_at_risk"])
    severity = row["severity"]

    # Default: require human verification
    decision = "HUMAN_REVIEW"
    reason = "Financial exception requires human verification."

    # Unknown / unsafe situation
    if exception_type not in [
        "PAYMENT_ORDER_MISMATCH",
        "SETTLEMENT_ANOMALY",
        "REFUND_ORDER_MISMATCH",
        "WEBHOOK_FAILURE"
    ]:

        decision = "BLOCK"
        reason = "Unknown exception type."

    # Webhook failures
    elif exception_type == "WEBHOOK_FAILURE":

        decision = "AUTO_APPROVE"
        reason = (
            "Non-monetary reconciliation action is permitted "
            "for webhook delivery failures."
        )

    # Payment/order mismatch
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

    # Settlement anomaly
    elif exception_type == "SETTLEMENT_ANOMALY":

        decision = "HUMAN_REVIEW"
        reason = (
            "Settlement discrepancy requires reconciliation "
            "against refunds, fees and adjustments."
        )

    # Refund mismatch
    elif exception_type == "REFUND_ORDER_MISMATCH":

        decision = "HUMAN_REVIEW"
        reason = (
            "Refund status affects customer liability and "
            "requires merchant verification."
        )

    return {
        "order_id": row["order_id"],
        "exception_type": exception_type,
        "amount_at_risk": amount,
        "severity": severity,
        "decision": decision,
        "reason": reason
    }


def run_policy_engine(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """
    Run the Policy Engine on an existing impact report.
    Used for the offline evaluation pipeline.
    """

    df = pd.read_csv(input_file)

    decisions = []

    for _, row in df.iterrows():
        decisions.append(evaluate_policy(row))

    decision_df = pd.DataFrame(decisions)

    decision_df.to_csv(
        output_file,
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
    print(output_file)

    return decision_df


if __name__ == "__main__":
    run_policy_engine()