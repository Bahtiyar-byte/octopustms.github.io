# Payment Terms

**Octopus TMS — operated by Digital Ronin LLC**
**Effective Date:** August 28, 2026
**Version:** 2026-08-28

---

## 1. What This Document Covers

These Payment Terms are part of your agreement with **Digital Ronin LLC** ("Octopus", "we", "us") and describe exactly how money moves between you and Octopus. They are incorporated into the Terms of Service and the Carrier Agreement. Refunds are covered by the separate **Refund & Cancellation Policy**.

- **"Load Fee"** — The flat per-load fee (currently $20.00 USD) charged on the Partnership plan when a load is created.
- **"Payment Method"** — The card you save to your account for Load Fee charges.
- **"Processor"** — Stripe, Inc. — the PCI-DSS Level 1 payment processor that stores your card and executes every charge.

## 2. The Price

> **$20 per load, charged to the carrier. Nothing else.** No monthly fee, no per-seat fee, no setup fee, no minimum. If you don't run a load, you don't pay.

- The Load Fee applies on the **Partnership plan**; accounts start on the Free plan and are never charged per load until they switch
- All prices are in **US dollars**
- If the Load Fee ever changes, you get at least **30 days' written notice** before the new price applies — no retroactive changes, ever

## 3. Your Card on File (Stored-Credential Authorization)

To use the Partnership plan you save a card with our Processor. By saving it you **authorize Octopus to charge that card automatically, without you being present at checkout, each time a load is created on your account** — one charge per load, at the price stated above, until you remove the card or leave the plan. This is the "off-session, card-on-file" authorization card networks require us to obtain in plain words.

- Your card number never touches Octopus servers — card entry and storage happen inside Stripe; we hold only a token and the last four digits
- You can replace or remove the card any time in **Settings → Billing**
- Removing your only card stops load creation on the Partnership plan (the charge happens first; no card, no charge, no load)

## 4. When the Charge Happens

The Load Fee is charged **at the moment a load is created**, before the load exists on the platform. Payment and load creation are atomic: if the charge fails, no load is created and you are told immediately. There is no invoice cycle, no accumulation, and no month-end surprise — every charge maps to one load you created that day.

- Each charge appears on your statement with our descriptor and is idempotent — a network retry can never double-charge a load
- A declined charge is not penalized; fix the card and create the load again
- Your full payment history is visible in **Settings → Billing → Payment History**

## 5. Failed Payments and Disputes

- If a charge fails, load creation stops with a clear error — nothing is created, nothing is owed
- If you believe a charge is wrong, contact us first: **ask@octopustms.com**. Genuine mistakes get refunded without ceremony
- A chargeback filed on a legitimately earned Load Fee may lead to account suspension while it is investigated, because chargebacks carry real cost and are meant for fraud, not disagreements we could have solved in one email

## 6. Taxes

The Load Fee is exclusive of any applicable taxes. Where a sales or similar tax applies to platform fees, it will be itemized on the charge. You are responsible for taxes on your own freight revenue — that is between you, your accountant, and the IRS.

## 7. About the Processor

Payments are processed by **Stripe, Inc.** Your use of the payment features is also subject to the Stripe Services Agreement (stripe.com/legal) and Stripe's Privacy Policy (stripe.com/privacy). We chose Stripe because your card is safer in their vault than in anyone else's — including ours.

## 8. Governing Law and Venue

These Payment Terms are governed by the laws of the State of Delaware, without regard to conflict-of-law rules. Any dispute arising from them will be brought exclusively in the state or federal courts located in Delaware, and both parties consent to their jurisdiction.

## 9. Contact

Billing questions: **ask@octopustms.com** or **private@thedigitalronin.com**.

## Version History

- **1.0** — August 28, 2026: First published version, describing the live Stripe card-on-file billing flow.
