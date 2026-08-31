import pandas as pd

GROUND_TRUTH = "../output/test_ground_truth.csv"
DETECTED = "../output/test_detected_exceptions.csv"

truth = pd.read_csv(GROUND_TRUTH)
detected = pd.read_csv(DETECTED)

# Only rows whose ground truth is NOT NONE are actual anomalies
truth_anomalies = truth[truth["ground_truth_exception"] != "NONE"].copy()

# Detected exceptions are already all anomalies
detected_anomalies = detected.copy()

# Match using order_id
truth_ids = set(truth_anomalies["order_id"])
detected_ids = set(detected_anomalies["order_id"])

TP = len(truth_ids & detected_ids)
FP = len(detected_ids - truth_ids)
FN = len(truth_ids - detected_ids)

precision = TP / (TP + FP) if (TP + FP) else 0
recall = TP / (TP + FN) if (TP + FN) else 0
f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall)
    else 0
)

print()
print("===================================")
print("       RAZORGUARD TEST EVALUATION")
print("===================================")

print(f"\nTest transactions       : {len(truth)}")
print(f"Ground-truth anomalies  : {len(truth_anomalies)}")
print(f"Detected exceptions     : {len(detected_anomalies)}")

print("\nConfusion:")
print(f"True Positives          : {TP}")
print(f"False Positives         : {FP}")
print(f"False Negatives         : {FN}")

print("\nMetrics:")
print(f"Precision               : {precision * 100:.2f}%")
print(f"Recall                  : {recall * 100:.2f}%")
print(f"F1 Score                : {f1 * 100:.2f}%")

print("\n===================================")