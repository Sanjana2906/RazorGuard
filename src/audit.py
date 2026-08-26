import pandas as pd
from pathlib import Path
from datetime import datetime

INPUT_FILE = Path("output/impact_report.csv")
OUTPUT_FILE = Path("output/audit_log.csv")

df = pd.read_csv(INPUT_FILE)

logs = []

for _, row in df.iterrows():

    timestamp = datetime.now().isoformat()

    # 1. Detection
    logs.append({
        "timestamp": timestamp,
        "order_id": row["order_id"],
        "stage": "DETECTION",
        "event": "EXCEPTION_DETECTED",
        "exception_type": row["exception_type"],
        "severity": row["severity"],
        "amount_at_risk": row["amount_at_risk"],
        "details": f"Detected {row['exception_type']}"
    })

    # 2. Evidence
    logs.append({
        "timestamp": timestamp,
        "order_id": row["order_id"],
        "stage": "EVIDENCE",
        "event": "EVIDENCE_COLLECTED",
        "exception_type": row["exception_type"],
        "severity": row["severity"],
        "amount_at_risk": row["amount_at_risk"],
        "details": row["evidence"]
    })

    # 3. Recommendation
    logs.append({
        "timestamp": timestamp,
        "order_id": row["order_id"],
        "stage": "RECOMMENDATION",
        "event": "ACTION_RECOMMENDED",
        "exception_type": row["exception_type"],
        "severity": row["severity"],
        "amount_at_risk": row["amount_at_risk"],
        "details": row["recommended_action"]
    })


audit_df = pd.DataFrame(logs)

audit_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("          RAZORGUARD AUDIT")
print("===================================")

print(f"\nExceptions audited: {len(df)}")
print(f"Audit events created: {len(audit_df)}")

print("\nEvent breakdown:")
print(audit_df["event"].value_counts())

print("\nExample audit trail:\n")

example_order = audit_df.iloc[0]["order_id"]

print(
    audit_df[
        audit_df["order_id"] == example_order
    ][
        [
            "stage",
            "event",
            "details"
        ]
    ].to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)