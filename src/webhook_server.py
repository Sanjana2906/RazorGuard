from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import razorpay
import json
import os

from live_orchestrator import process_live_transaction

load_dotenv()

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

WEBHOOK_LOG = "output/live_webhooks.jsonl"
EVENT_LOG = "output/processed_webhook_ids.txt"

os.makedirs("output", exist_ok=True)


def verify_signature(raw_body, signature):
    """Verify that the webhook really came from Razorpay."""

    if not WEBHOOK_SECRET or not signature:
        return False

    try:
        razorpay.Client().utility.verify_webhook_signature(
            raw_body,
            signature,
            WEBHOOK_SECRET
        )
        return True

    except Exception:
        return False


def already_processed(event_id):
    """Prevent processing the same Razorpay event twice."""

    if not event_id:
        return False

    if not os.path.exists(EVENT_LOG):
        return False

    with open(EVENT_LOG, "r", encoding="utf-8") as f:
        return event_id in {
            line.strip()
            for line in f
        }


def mark_processed(event_id):

    if event_id:

        with open(EVENT_LOG, "a", encoding="utf-8") as f:
            f.write(event_id + "\n")


@app.route("/webhook", methods=["POST"])
def webhook():

    # ==================================================
    # 1. RAW REQUEST
    # ==================================================

    raw_body = request.get_data(as_text=True)

    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    event_id = request.headers.get(
        "x-razorpay-event-id"
    )

    # ==================================================
    # 2. SECURITY
    # ==================================================

    if not verify_signature(
        raw_body,
        signature
    ):

        print("\n❌ INVALID WEBHOOK SIGNATURE")

        return jsonify({
            "status": "invalid_signature"
        }), 400

    # ==================================================
    # 3. IDEMPOTENCY
    # ==================================================

    if already_processed(event_id):

        print("\n⚠️ DUPLICATE WEBHOOK IGNORED")

        print(
            "Event ID:",
            event_id
        )

        return jsonify({
            "status": "duplicate_ignored"
        }), 200

    # ==================================================
    # 4. PARSE EVENT
    # ==================================================

    try:

        payload = json.loads(raw_body)

    except json.JSONDecodeError:

        print("\n❌ INVALID JSON")

        return jsonify({
            "status": "invalid_json"
        }), 400

    event = payload.get(
        "event",
        "unknown"
    )

    # ==================================================
    # 5. DISPLAY EVENT
    # ==================================================

    print("\n" + "=" * 60)
    print("🚨 RAZORGUARD WEBHOOK RECEIVED")
    print("=" * 60)

    print(
        "Time:",
        datetime.now().isoformat()
    )

    print(
        "Event:",
        event
    )

    print(
        "Event ID:",
        event_id
    )

    # ==================================================
    # 6. EXTRACT PAYMENT
    # ==================================================

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if payment:

        print("\nPAYMENT")
        print("-" * 30)

        print(
            "Payment ID:",
            payment.get("id")
        )

        print(
            "Order ID:",
            payment.get("order_id")
        )

        print(
            "Amount: ₹",
            payment.get("amount", 0) / 100
        )

        print(
            "Status:",
            payment.get("status")
        )

        print(
            "Method:",
            payment.get("method")
        )

    # ==================================================
    # 7. RAZORGUARD LIVE PIPELINE
    # ==================================================

    if event == "payment.captured" and payment:

        order_id = payment.get(
            "order_id"
        )

        payment_id = payment.get(
            "id"
        )

        payment_state = payment.get(
            "status",
            ""
        ).upper()

        payment_amount = (
            payment.get("amount", 0) / 100
        )

        print("\n" + "=" * 60)
        print("🔍 RAZORGUARD LIVE PIPELINE")
        print("=" * 60)

        # ------------------------------------------------
        # DEMO MERCHANT STATE
        # ------------------------------------------------
        # Razorpay = CAPTURED
        # Merchant DB = UNPAID
        #
        # This intentionally creates the cross-system
        # inconsistency that RazorGuard detects.

        merchant_order_state = "UNPAID"

        transaction, exceptions = (
            process_live_transaction(
                order_id=order_id,
                payment_id=payment_id,
                payment_state=payment_state,
                payment_amount=payment_amount,
                merchant_order_state=merchant_order_state,
                webhook_status="RECEIVED"
            )
        )

        if exceptions:

            print("\n🚨 LIVE RAZORGUARD ALERT")

            for exception in exceptions:

                print(
                    "Exception:",
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

        else:

            print(
                "\n✓ No RazorGuard exception"
            )

    # ==================================================
    # 8. SAVE AUDIT RECORD
    # ==================================================

    record = {

        "received_at":
            datetime.now().isoformat(),

        "event_id":
            event_id,

        "event":
            event,

        "payload":
            payload
    }

    with open(
        WEBHOOK_LOG,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(record) + "\n"
        )

    # ==================================================
    # 9. MARK EVENT PROCESSED
    # ==================================================

    mark_processed(event_id)

    print("\n✓ Signature verified")
    print("✓ Event accepted")
    print("✓ Audit record stored")
    print("✓ Event ID recorded")

    return jsonify({
        "status": "received"
    }), 200


if __name__ == "__main__":

    print("=" * 60)
    print("       RAZORGUARD SECURE WEBHOOK SERVER")
    print("=" * 60)

    print(
        "Listening on port 5000..."
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000
    )