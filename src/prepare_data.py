import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

# Load the 3 Olist datasets
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")

print("Orders:", len(orders))
print("Payments:", len(payments))
print("Items:", len(items))

# ---------------------------------------------------------
# 1. Calculate total order value from order items
# ---------------------------------------------------------

order_values = (
    items.groupby("order_id")
    .agg(
        item_value=("price", "sum"),
        freight_value=("freight_value", "sum")
    )
    .reset_index()
)

order_values["expected_amount"] = (
    order_values["item_value"] +
    order_values["freight_value"]
)

# ---------------------------------------------------------
# 2. Calculate total payment value for each order
# ---------------------------------------------------------

payment_values = (
    payments.groupby("order_id")
    .agg(
        payment_amount=("payment_value", "sum")
    )
    .reset_index()
)

# ---------------------------------------------------------
# 3. Merge order + payment + item information
# ---------------------------------------------------------

df = orders.merge(
    order_values,
    on="order_id",
    how="inner"
)

df = df.merge(
    payment_values,
    on="order_id",
    how="inner"
)

# ---------------------------------------------------------
# 4. Keep useful fields
# ---------------------------------------------------------

df = df[
    [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "expected_amount",
        "payment_amount"
    ]
].copy()

# ---------------------------------------------------------
# 5. Create merchant-side state
# ---------------------------------------------------------

df["merchant_order_state"] = df["order_status"].map(
    {
        "delivered": "PAID",
        "shipped": "PAID",
        "invoiced": "PAID",
        "processing": "PAID",
        "approved": "PAID",
        "created": "UNPAID",
        "canceled": "CANCELLED",
        "unavailable": "CANCELLED"
    }
).fillna("UNKNOWN")

# ---------------------------------------------------------
# 6. Create a simplified payment state
# ---------------------------------------------------------

df["payment_state"] = "CAPTURED"

# ---------------------------------------------------------
# 7. Basic amount consistency check
# ---------------------------------------------------------

df["amount_difference"] = (
    df["payment_amount"] - df["expected_amount"]
).round(2)

df["amount_match"] = (
    df["amount_difference"].abs() < 0.01
)

# ---------------------------------------------------------
# 8. Select 500 records
# ---------------------------------------------------------

df = df.drop_duplicates("order_id")

df = df.sample(
    n=min(500, len(df)),
    random_state=42
).reset_index(drop=True)

# ---------------------------------------------------------
# 9. Add RazorGuard fields
# ---------------------------------------------------------

df["payment_id"] = "pay_" + df.index.astype(str).str.zfill(6)

df["settlement_status"] = "SETTLED"

df["settlement_amount"] = df["payment_amount"]

df["refund_status"] = "NOT_REFUNDED"

df["refund_amount"] = 0.0

df["webhook_status"] = "DELIVERED"

# ---------------------------------------------------------
# 10. Save
# ---------------------------------------------------------

output_file = OUTPUT_DIR / "razorguard_base.csv"

df.to_csv(output_file, index=False)

print("\nRazorGuard dataset created!")
print("Records:", len(df))
print("File:", output_file)

print("\nColumns:")
for column in df.columns:
    print(" -", column)

print("\nFirst 5 records:")
print(df.head())