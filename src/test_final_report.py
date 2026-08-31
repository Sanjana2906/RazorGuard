import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

EXCEPTIONS_FILE = BASE_DIR / "output" / "test_detected_exceptions.csv"
STATES_FILE = BASE_DIR / "output" / "test_financial_states.csv"
IMPACT_FILE = BASE_DIR / "output" / "test_impact_report.csv"
POLICY_FILE = BASE_DIR / "output" / "test_policy_decisions.csv"
AI_FILE = BASE_DIR / "output" / "test_ai_explanations.csv"
AUDIT_FILE = BASE_DIR / "output" / "test_audit_log.csv"

OUTPUT_FILE = BASE_DIR / "output" / "razorguard_test_final_report.csv"


exceptions = pd.read_csv(EXCEPTIONS_FILE)
states = pd.read_csv(STATES_FILE)
impact = pd.read_csv(IMPACT_FILE)
policy = pd.read_csv(POLICY_FILE)
ai = pd.read_csv(AI_FILE)
audit = pd.read_csv(AUDIT_FILE)


# --------------------------------------------------
# Merge the complete pipeline
# --------------------------------------------------

report = exceptions[
    [
        "order_id",
        "exception_type",
        "severity",
        "amount_affected",
        "reason"
    ]
].copy()


report = report.merge(
    states[
        [
            "order_id",
            "overall_state",
            "financial_exposure"
        ]
    ],
    on="order_id",
    how="left"
)


report = report.merge(
    impact[
        [
            "order_id",
            "amount_at_risk",
            "evidence",
            "likely_cause",
            "recommended_action"
        ]
    ],
    on="order_id",
    how="left"
)


report = report.merge(
    policy[
        [
            "order_id",
            "decision"
        ]
    ],
    on="order_id",
    how="left"
)


report = report.merge(
    ai[
        [
            "order_id",
            "explanation",
            "recommendation"
        ]
    ],
    on="order_id",
    how="left"
)


# --------------------------------------------------
# Save final report
# --------------------------------------------------

report.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Display final results
# --------------------------------------------------

print("\n===================================")
print("   RAZORGUARD HELD-OUT FINAL REPORT")
print("===================================\n")

print(f"Exceptions included: {len(report)}")

print("\nException breakdown:")
print(
    report["exception_type"]
    .value_counts()
)

print(
    f"\nTotal amount at risk: "
    f"₹{report['amount_at_risk'].sum():.2f}"
)

print("\nPolicy decisions:")
print(
    report["decision"]
    .value_counts(dropna=False)
)

print("\nFinancial states:")
print(
    report["overall_state"]
    .value_counts()
)

print("\nAudit events:")
print(
    audit["event"]
    .value_counts()
)

print("\nTop exceptions:")

print(
    report[
        [
            "order_id",
            "exception_type",
            "severity",
            "amount_at_risk",
            "overall_state",
            "decision"
        ]
    ]
    .sort_values(
        "amount_at_risk",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)