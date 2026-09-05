# RazorGuard

### AI-Assisted Financial Consistency & Exception Control

> Razorpay tells you what happened. RazorGuard tells you when your business disagrees.

RazorGuard is an AI-assisted financial control layer that detects inconsistencies between payment-system events and merchant business states.

Instead of only checking whether a payment succeeded, RazorGuard cross-checks payment, order, settlement, refund, and webhook states to identify financial exceptions, quantify their impact, apply bounded policies, explain the issue, and maintain an audit trail.

---

## Problem

A successful payment does not always mean that the merchant's internal transaction state is correct.

For example:

**Payment System**
- Payment: `CAPTURED`
- Amount: ₹100

**Merchant System**
- Order: `UNPAID`

This state mismatch can lead to duplicate payment requests, incorrect order fulfillment, refund liability, reconciliation problems, and financial leakage.

Traditional payment dashboards show the payment state, but merchants still need to reconcile that state with their own business systems.

---

## Solution

RazorGuard acts as a financial consistency layer between payment infrastructure and merchant systems.

It:

1. Receives payment events and transaction data.
2. Normalizes payment and merchant states.
3. Detects inconsistencies using explicit financial rules.
4. Quantifies the financial exposure.
5. Collects supporting evidence.
6. Applies bounded policies to determine the appropriate action.
7. Generates human-readable explanations and recommendations.
8. Records an auditable trail of the decision.

---

## Architecture


 <img width="891" height="597" alt="image" src="https://github.com/user-attachments/assets/c6271877-edfc-4818-a416-d695432a8343" />
