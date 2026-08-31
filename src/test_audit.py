import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "test_ai_explanations.csv"
OUTPUT_FILE = BASE_DIR / "output" / "test_audit_log.csv"

df = pd.read_csv(INPUT_FILE)

audit_events = []

for _, row in df.iterrows():

    order_id = row["order_id"]
    exception_type = row["exception_type"]
    amount = float(row["amount_at_risk"])
    decision = row["policy_decision"]

    # ---------------------------------------------
    # 1. Detection event
    # ---------------------------------------------

    audit_events.append({
        "order_id": order_id,
        "stage": "DETECTION",
        "event": "EXCEPTION_DETECTED",
        "details": f"Detected {exception_type}",
    })

    # ---------------------------------------------
    # 2. Evidence event
    # ---------------------------------------------

    audit_events.append({
        "order_id": order_id,
        "stage": "EVIDENCE",
        "event": "EVIDENCE_COLLECTED",
        "details": (
            f"Exception={exception_type}; "
            f"Amount affected=₹{amount:.2f}"
        ),
    })

    # ---------------------------------------------
    # 3. Recommendation event
    # ---------------------------------------------

    audit_events.append({
        "order_id": order_id,
        "stage": "RECOMMENDATION",
        "event": "ACTION_RECOMMENDED",
        "details": (
            f"Policy decision={decision}; "
            f"Recommendation={row['recommendation']}"
        ),
    })


audit_df = pd.DataFrame(audit_events)

audit_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("       RAZORGUARD TEST AUDIT")
print("===================================\n")

print(f"Exceptions audited: {len(df)}")
print(f"Audit events created: {len(audit_df)}")

print("\nEvent breakdown:")
print(audit_df["event"].value_counts())

print("\nExample audit trail:")

print(
    audit_df
    .head(3)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)