import os
from dotenv import load_dotenv
import razorpay

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(key_id, key_secret))

order = client.order.create({
    "amount": 10000,
    "currency": "INR",
    "receipt": "razorguard_webhook_test_001",
    "notes": {
        "project": "RazorGuard",
        "test": "webhook"
    }
})

order_id = order["id"]

html = f"""<!DOCTYPE html>
<html>
<head>
    <title>RazorGuard Test Payment</title>
</head>
<body>
    <h1>RazorGuard Test Payment</h1>
    <p>Amount: ?100</p>
    <button id="pay">Pay ?100 (Test Mode)</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
        document.getElementById("pay").onclick = function() {{
            var options = {{
                "key": "{key_id}",
                "amount": "10000",
                "currency": "INR",
                "name": "RazorGuard",
                "description": "Webhook Test Payment",
                "order_id": "{order_id}",
                "handler": function(response) {{
                    alert(
                        "PAYMENT SUCCESS\\n\\n" +
                        "Payment ID: " + response.razorpay_payment_id + "\\n" +
                        "Order ID: " + response.razorpay_order_id
                    );
                }}
            }};

            var rzp = new Razorpay(options);
            rzp.open();
        }};
    </script>
</body>
</html>
"""

with open("test_checkout.html", "w", encoding="utf-8") as f:
    f.write(html)

print("=" * 60)
print("RAZORGUARD TEST PAYMENT")
print("=" * 60)
print("Order ID:", order_id)
print("Amount: ?100")
print()
print("Checkout created:")
print("test_checkout.html")
print()
print("Open this file in your browser and click:")
print("Pay ?100 (Test Mode)")
