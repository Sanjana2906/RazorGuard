from live_pipeline import run_live_detection

from impact_engine import (
    generate_evidence,
    determine_cause,
    recommend_action,
    calculate_severity
)

from policy_engine import evaluate_policy
from ai_explainer import generate_explanation
from audit import create_audit_events

import pandas as pd


def process_live_transaction(
    order_id,
    payment_id=None,
    payment_state=None,
    payment_amount=None,
    merchant_order_state="UNPAID",
    webhook_status="RECEIVED"
):
    """
    Process one live Razorpay transaction through the
    complete RazorGuard pipeline.

    Pipeline:
        Detection
        -> Financial State
        -> Impact
        -> Policy
        -> AI Explanation
        -> Audit Trail
    """

    # ==========================================================
    # 1. GET TRANSACTION DATA
    # ==========================================================

    if (
        payment_id is not None
        and payment_state is not None
        and payment_amount is not None
    ):

        transaction = {
            "order_id": order_id,
            "payment_id": payment_id,
            "payment_state": str(payment_state).upper(),
            "payment_amount": float(payment_amount),
            "merchant_order_state": str(
                merchant_order_state
            ).upper(),
            "webhook_status": webhook_status
        }

    else:

        transaction, exceptions = run_live_detection(
            order_id
        )

        return transaction, exceptions

    # ==========================================================
    # 2. CROSS-SYSTEM EXCEPTION DETECTION
    # ==========================================================

    exceptions = []

    if (
        transaction["payment_state"] == "CAPTURED"
        and transaction["merchant_order_state"]
        in ["UNPAID", "PENDING"]
    ):

        exceptions.append({
            "order_id": transaction["order_id"],
            "exception_type": "PAYMENT_ORDER_MISMATCH",
            "severity": "HIGH",
            "amount_affected": abs(
                transaction["payment_amount"]
            ),
            "reason": (
                "Payment captured but merchant order "
                "is not marked as paid"
            )
        })

    # ==========================================================
    # 3. FINANCIAL STATE MACHINE
    # ==========================================================

    if (
        transaction["payment_state"] == "CAPTURED"
        and transaction["merchant_order_state"] == "UNPAID"
    ):

        financial_state = "PAYMENT_CAPTURED_ORDER_UNPAID"

    elif (
        transaction["payment_state"] == "CAPTURED"
        and transaction["merchant_order_state"] == "PENDING"
    ):

        financial_state = "PAYMENT_CAPTURED_ORDER_PENDING"

    else:

        financial_state = "CONSISTENT"

    transaction["financial_state"] = financial_state

    # ==========================================================
    # 4. IMPACT ENGINE
    # ==========================================================

    if exceptions:

        exception = exceptions[0]

        # Convert live transaction into the format
        # expected by the existing Impact Engine.

        impact_data = {
            "order_id": transaction["order_id"],
            "exception_type": exception["exception_type"],
            "severity": exception["severity"],

            "amount_affected":
                exception["amount_affected"],

            "amount_at_risk":
                abs(float(exception["amount_affected"])),

            "payment_amount":
                transaction["payment_amount"],

            "payment_state":
                transaction["payment_state"],

            "merchant_order_state":
                transaction["merchant_order_state"],

            "settlement_status":
                "NOT_AVAILABLE",

            "settlement_amount":
                0,

            "refund_status":
                "NONE",

            "refund_amount":
                0,

            "webhook_status":
                transaction["webhook_status"]
        }

        impact_row = pd.Series(impact_data)

        # Generate evidence
        impact_evidence = generate_evidence(
            impact_row
        )

        # Determine likely cause
        impact_cause = determine_cause(
            impact_row
        )

        # Recommend action
        impact_action = recommend_action(
            impact_row
        )

        # Calculate severity
        impact_severity = calculate_severity(
            impact_row
        )

        # Store complete impact result
        transaction["impact"] = {

            "amount_at_risk":
                round(
                    abs(
                        float(
                            exception["amount_affected"]
                        )
                    ),
                    2
                ),

            "evidence":
                impact_evidence,

            "likely_cause":
                impact_cause,

            "recommended_action":
                impact_action,

            "severity":
                impact_severity
        }

        # Use Impact Engine's severity as the
        # source of truth for downstream stages.
        exception["severity"] = impact_severity

        print("\nIMPACT ENGINE")
        print("-" * 30)

        print(
            "Amount at risk: ₹",
            transaction["impact"]["amount_at_risk"]
        )

        print(
            "Evidence:",
            impact_evidence
        )

        print(
            "Likely cause:",
            impact_cause
        )

        print(
            "Recommended action:",
            impact_action
        )

        print(
            "Severity:",
            impact_severity
        )

    # ==========================================================
    # 5. POLICY ENGINE
    # ==========================================================

    if exceptions:

        exception = exceptions[0]

        policy_row = {
            "order_id":
                transaction["order_id"],

            "exception_type":
                exception["exception_type"],

            "amount_at_risk":
                transaction["impact"]["amount_at_risk"],

            "severity":
                exception["severity"]
        }

        policy_decision = evaluate_policy(
            policy_row
        )

        transaction["policy"] = {

            "decision":
                policy_decision["decision"],

            "reason":
                policy_decision["reason"]
        }

        print("\nPOLICY ENGINE")
        print("-" * 30)

        print(
            "Decision:",
            policy_decision["decision"]
        )

        print(
            "Reason:",
            policy_decision["reason"]
        )

    # ==========================================================
    # 6. AI EXPLAINER
    # ==========================================================

    if exceptions:

        exception = exceptions[0]

        explanation_row = {

            "order_id":
                transaction["order_id"],

            "exception_type":
                exception["exception_type"],

            "amount_at_risk":
                transaction["impact"]["amount_at_risk"],

            "decision":
                policy_decision["decision"]
        }

        ai_result = generate_explanation(
            explanation_row
        )

        transaction["ai_explanation"] = {

            "explanation":
                ai_result["explanation"],

            "recommendation":
                ai_result["recommendation"]
        }

        print("\nAI EXPLAINER")
        print("-" * 30)

        print(
            "Explanation:",
            ai_result["explanation"]
        )

        print(
            "Recommendation:",
            ai_result["recommendation"]
        )

    # ==========================================================
    # 7. AUDIT TRAIL
    # ==========================================================

    if exceptions:

        exception = exceptions[0]

        audit_events = create_audit_events(

            order_id=
                transaction["order_id"],

            exception_type=
                exception["exception_type"],

            severity=
                exception["severity"],

            amount_at_risk=
                transaction["impact"]["amount_at_risk"],

            evidence=
                transaction["impact"]["evidence"],

            recommended_action=
                transaction["impact"]["recommended_action"]
        )

        transaction["audit_trail"] = audit_events

        print("\nAUDIT TRAIL")
        print("-" * 30)

        for event in audit_events:

            print(
                event["event"],
                "|",
                event["details"]
            )

        print(
            "\nAudit events created:",
            len(audit_events)
        )

    # ==========================================================
    # 8. FINAL DISPLAY
    # ==========================================================

    print("\n" + "=" * 60)
    print("       RAZORGUARD LIVE ORCHESTRATOR")
    print("=" * 60)

    print("\nTransaction")
    print("-" * 30)

    print(
        "Order ID:",
        transaction["order_id"]
    )

    print(
        "Payment ID:",
        transaction["payment_id"]
    )

    print(
        "Payment State:",
        transaction["payment_state"]
    )

    print(
        "Merchant State:",
        transaction["merchant_order_state"]
    )

    print(
        "Amount: ₹",
        transaction["payment_amount"]
    )

    print("\nFINANCIAL STATE")
    print("-" * 30)

    print(
        "State:",
        transaction["financial_state"]
    )

    if exceptions:

        print("\n🚨 EXCEPTION DETECTED")

        for exception in exceptions:

            print(
                "\nType:",
                exception["exception_type"]
            )

            print(
                "Severity:",
                exception["severity"]
            )

            print(
                "Amount at risk: ₹",
                exception["amount_affected"]
            )

            print(
                "Reason:",
                exception["reason"]
            )

    else:

        print("\n✓ No exception detected")

    return transaction, exceptions


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    ORDER_ID = "order_TXvgHrM484ESVw"

    transaction, exceptions = process_live_transaction(

        order_id=ORDER_ID,

        payment_id="pay_TXvjYRMoRBQ12s",

        payment_state="CAPTURED",

        payment_amount=100.0,

        merchant_order_state="UNPAID",

        webhook_status="RECEIVED"
    )

    print("\n" + "=" * 60)
    print("       LIVE ORCHESTRATOR RESULT")
    print("=" * 60)

    print(
        "\nTransaction processed:",
        transaction["order_id"]
    )

    print(
        "Exceptions detected:",
        len(exceptions)
    )

    print(
        "Financial state:",
        transaction["financial_state"]
    )

    if exceptions:

        exception = exceptions[0]

        print(
            "\nException type:",
            exception["exception_type"]
        )

        print(
            "Severity:",
            exception["severity"]
        )

        print(
            "Amount at risk: ₹",
            exception["amount_affected"]
        )

        print(
            "\n✓ Live transaction successfully "
            "entered RazorGuard"
        )

    else:

        print("\n✓ No exception detected")