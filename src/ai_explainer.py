import pandas as pd
from pathlib import Path


INPUT_FILE = Path("output/impact_report.csv")
POLICY_FILE = Path("output/policy_decisions.csv")
OUTPUT_FILE = Path("output/ai_explanations.csv")


def generate_explanation(row):
    """
    Generate a human-readable explanation and recommendation
    for one RazorGuard exception.
    """

    exception_type = row["exception_type"]
    amount = float(row["amount_at_risk"])

    if exception_type == "PAYMENT_ORDER_MISMATCH":

        explanation = (
            f"The payment of ₹{amount:.2f} appears to have been "
            "captured successfully, but the merchant's internal "
            "order state remains unpaid. This suggests that the "
            "merchant-side order update may not have completed."
        )

        recommendation = (
            "Verify the payment against the merchant order "
            "before requesting another payment."
        )

    elif exception_type == "SETTLEMENT_ANOMALY":

        explanation = (
            f"The captured payment amount differs from the "
            f"settlement amount, creating an apparent exposure "
            f"of ₹{amount:.2f}. The difference may be explained "
            "by refunds, fees, adjustments or settlement timing."
        )

        recommendation = (
            "Reconcile the settlement against payment, refund, "
            "fee and adjustment records."
        )

    elif exception_type == "REFUND_ORDER_MISMATCH":

        explanation = (
            f"The merchant order indicates a cancellation while "
            f"the expected refund of ₹{amount:.2f} has not completed. "
            "This may create an outstanding customer liability."
        )

        recommendation = (
            "Verify refund processing status and investigate "
            "the outstanding refund."
        )

    elif exception_type == "WEBHOOK_FAILURE":

        explanation = (
            f"The payment appears successful, but the expected "
            f"webhook was not delivered. The affected transaction "
            f"value is ₹{amount:.2f}. This may leave the merchant "
            "system out of sync with the payment system."
        )

        recommendation = (
            "Verify webhook delivery and reconcile the merchant "
            "transaction state."
        )

    else:

        explanation = (
            "The transaction contains an unresolved financial "
            "state inconsistency."
        )

        recommendation = (
            "Send the transaction for manual investigation."
        )

    return {
        "explanation": explanation,
        "recommendation": recommendation
    }


def run_ai_explainer(
    input_file=INPUT_FILE,
    policy_file=POLICY_FILE,
    output_file=OUTPUT_FILE
):
    """
    Run AI Explainer on the offline impact + policy reports.
    """

    impact = pd.read_csv(input_file)
    policy = pd.read_csv(policy_file)

    df = impact.merge(
        policy[
            [
                "order_id",
                "decision",
                "reason"
            ]
        ],
        on="order_id",
        how="left"
    )

    results = []

    for _, row in df.iterrows():

        generated = generate_explanation(row)

        results.append({
            "order_id": row["order_id"],
            "exception_type": row["exception_type"],
            "amount_at_risk": row["amount_at_risk"],
            "policy_decision": row["decision"],
            "explanation": generated["explanation"],
            "recommendation": generated["recommendation"]
        })

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        output_file,
        index=False
    )

    print("\n===================================")
    print("       RAZORGUARD AI EXPLAINER")
    print("===================================")

    print(f"\nExceptions explained: {len(result_df)}")

    print("\nExample explanation:\n")
    print(result_df.iloc[0].to_string())

    print("\nSaved to:")
    print(output_file)

    return result_df


if __name__ == "__main__":
    run_ai_explainer()