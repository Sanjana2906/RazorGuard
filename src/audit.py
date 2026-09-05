import pandas as pd
from pathlib import Path
from datetime import datetime


INPUT_FILE = Path("output/impact_report.csv")
OUTPUT_FILE = Path("output/audit_log.csv")


def create_audit_events(
    order_id,
    exception_type,
    severity,
    amount_at_risk,
    evidence,
    recommended_action
):
    """
    Create the three core RazorGuard audit events
    for one financial exception.
    """

    timestamp = datetime.now().isoformat()

    logs = []

    # 1. Detection
    logs.append({
        "timestamp": timestamp,
        "order_id": order_id,
        "stage": "DETECTION",
        "event": "EXCEPTION_DETECTED",
        "exception_type": exception_type,
        "severity": severity,
        "amount_at_risk": amount_at_risk,
        "details": f"Detected {exception_type}"
    })

    # 2. Evidence
    logs.append({
        "timestamp": timestamp,
        "order_id": order_id,
        "stage": "EVIDENCE",
        "event": "EVIDENCE_COLLECTED",
        "exception_type": exception_type,
        "severity": severity,
        "amount_at_risk": amount_at_risk,
        "details": evidence
    })

    # 3. Recommendation
    logs.append({
        "timestamp": timestamp,
        "order_id": order_id,
        "stage": "RECOMMENDATION",
        "event": "ACTION_RECOMMENDED",
        "exception_type": exception_type,
        "severity": severity,
        "amount_at_risk": amount_at_risk,
        "details": recommended_action
    })

    return logs


def run_audit(
    input_file=INPUT_FILE,
    output_file=OUTPUT_FILE
):
    """
    Run the audit engine on the offline impact report.
    """

    df = pd.read_csv(input_file)

    logs = []

    for _, row in df.iterrows():

        logs.extend(
            create_audit_events(
                order_id=row["order_id"],
                exception_type=row["exception_type"],
                severity=row["severity"],
                amount_at_risk=row["amount_at_risk"],
                evidence=row["evidence"],
                recommended_action=row["recommended_action"]
            )
        )

    audit_df = pd.DataFrame(logs)

    audit_df.to_csv(
        output_file,
        index=False
    )

    print("\n===================================")
    print("          RAZORGUARD AUDIT")
    print("===================================")

    print(f"\nExceptions audited: {len(df)}")
    print(f"Audit events created: {len(audit_df)}")

    print("\nEvent breakdown:")
    print(audit_df["event"].value_counts())

    print("\nSaved to:")
    print(output_file)

    return audit_df


if __name__ == "__main__":
    run_audit()