import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

steps = [
    "prepare_data.py",
    "detector.py",
    "state_machine.py",
    "impact_engine.py",
    "policy_engine.py",
    "ai_explainer.py",
    "audit.py"
]

print("\n===================================")
print("          RAZORGUARD")
print("   FINANCIAL CONSISTENCY ENGINE")
print("===================================\n")

for filename in steps:

    script = BASE_DIR / "src" / filename

    print(f"\n>>> Running {script}")

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(BASE_DIR)
    )

    if result.returncode != 0:
        print(f"\nERROR: {filename} failed.")
        sys.exit(1)

print("\n===================================")
print("       RAZORGUARD COMPLETE")
print("===================================")

print("\nOutputs generated:")
print("  ✓ detected_exceptions.csv")
print("  ✓ financial_states.csv")
print("  ✓ impact_report.csv")
print("  ✓ policy_decisions.csv")
print("  ✓ ai_explanations.csv")
print("  ✓ audit_log.csv")