import pandas as pd
from pathlib import Path

# Always use RazorGuard root/output regardless of current directory
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

exceptions = pd.read_csv(
    OUTPUT_DIR / "test_detected_exceptions.csv"
)

states = pd.read_csv(
    OUTPUT_DIR / "financial_states.csv"
)

impact = pd.read_csv(
    OUTPUT_DIR / "impact_report.csv"
)

policy = pd.read_csv(
    OUTPUT_DIR / "policy_decisions.csv"
)

ai = pd.read_csv(
    OUTPUT_DIR / "ai_explanations.csv"
)

# --------------------------------------------------
# Merge all RazorGuard results
# --------------------------------------------------

report = exceptions.merge(
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

# Remove accidental duplicates
report = report.drop_duplicates(
    subset=["order_id", "exception_type"]
)

# --------------------------------------------------
# Sort by severity
# --------------------------------------------------

severity_order = {
    "HIGH": 0,
    "MEDIUM": 1,
    "LOW": 2
}

report["_severity_rank"] = (
    report["severity"]
    .map(severity_order)
    .fillna(3)
)

report = (
    report
    .sort_values("_severity_rank")
    .drop(columns=["_severity_rank"])
)

# --------------------------------------------------
# Save final report
# --------------------------------------------------

output_file = OUTPUT_DIR / "razorguard_final_report.csv"

report.to_csv(
    output_file,
    index=False
)

# --------------------------------------------------
# Display summary
# --------------------------------------------------

print("\n===================================")
print("      RAZORGUARD FINAL REPORT")
print("===================================")

print(f"\nExceptions included: {len(report)}")

print("\nException breakdown:")
print(
    report["exception_type"]
    .value_counts()
)

total_at_risk = (
    report["amount_at_risk"]
    .fillna(0)
    .sum()
)

print(
    f"\nTotal amount at risk: ₹{total_at_risk:.2f}"
)

print("\nPolicy decisions:")
print(
    report["decision"]
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
    .head(10)
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)

