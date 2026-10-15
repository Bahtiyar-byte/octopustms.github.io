# Privacy Policy

**Effective Date: August 28, 2026**

> Mirror of the shipped document. The canonical source is
> `frontend/src/features/legal/components/PrivacyPolicyContent.tsx`, rendered at `/legal/privacy-policy`.
> After editing either one, update the other and run `npm run legal:pdf` from `frontend/`.

## 1. Introduction

Octopus TMS, operated by Digital Ronin LLC ("Octopus", "we", "us"), runs a transportation management platform for motor carriers. This policy explains what we collect, why, who we share it with, and what you can do about it. Plain language, no games.

**The short version:** we use your data to run the platform for you. We don't sell it, we don't rent it, we don't hand it to advertisers, and we don't train AI models on it.

## 2. What We Collect

### 2.1 Business Information
- Company name, business address, phone and email
- DOT and MC numbers, operating authority and FMCSA rating, where you provide them
- EIN / tax ID — **stored encrypted**
- Insurance carriers, policy numbers, coverage amounts and expiry dates
- Bank account and routing numbers used for settlements — **stored encrypted**
- Factoring company details, if you use one

### 2.2 People on Your Account
- Names, emails, phone numbers and roles for your admins, dispatchers and drivers
- Passwords, stored only as salted hashes — we can't read them
- Driver records: license details, emergency contacts, pay settings and assignment history

### 2.3 Trip Location History

Precise location is sensitive data and we treat it that way:

- The driver app collects location **only while a driver is running a load they consented to**
- No active consented load means no location history is written — off-duty movement is not tracked
- A driver can decline or withdraw tracking consent from the app
- We use it to deliver load tracking, ETAs and proof of service, **and to defend delivery, detention and cargo claims** — the trip record is evidence, and disputes surface years after the freight moves. Nothing else
- We keep it for **5 years from the date of the trip**, then delete it (§7)

### 2.4 Operational Data
- Loads, bookings, dispatch assignments and status history
- Documents you upload or we generate — rate confirmations, BOLs, PODs, invoices
- Broker and customer contact details you enter
- Messages and notifications sent through the platform

### 2.5 Financial Data
- Invoices, settlements, expenses and factoring submissions
- Your subscription plan and billing history
- Card details go directly to Stripe. **We never receive or store your full card number**

### 2.6 Technical Data
- IP address, browser and device information
- Login and session activity, for security and audit
- Error logs and usage patterns, used to fix and improve the platform

## 3. Why We Use It

### 3.1 Running the Service
- Searching and booking loads, dispatching drivers, tracking freight
- Generating documents and invoices, submitting to factoring, calculating settlements
- Billing you, and supporting you when something breaks

### 3.2 Keeping It Safe and Working
- Detecting fraud and abuse, and investigating security incidents
- Diagnosing failures and improving features, using aggregated usage data

### 3.3 What We Never Do
- Sell or rent your data, or share it for cross-context behavioral advertising
- Use your data to train generalized or non-personalized AI or ML models
- Use it for credit or lending decisions
- Show your loads, rates or customers to another carrier on the platform

## 4. Who Sees It

### 4.1 Service Providers

These providers process data on our behalf, only as needed to deliver the Service:

- **Amazon Web Services** — hosting, database and document storage (United States)
- **Stripe** — payment processing and payouts
- **DAT** — load board search and booking
- **Intuit QuickBooks** — invoice and customer sync, only if you connect it
- **Google / Gmail** — sending email from your own address, only if you connect it
- **Firebase (Google)** — driver app push notifications and messaging
- **Twilio** — SMS notifications
- **Mapbox** — map rendering and tracking display
- Email delivery providers for transactional mail

### 4.2 People You Choose to Share With
- Brokers and shippers on the loads you book, and on the documents you send them
- Your factoring company, when you submit an invoice packet
- **Public tracking links.** When you generate one for a load, anyone holding that link can see that load's status and location updates. Send them deliberately

### 4.3 Legal

We disclose data when we're legally required to, or to:

- Comply with a valid legal process
- Investigate fraud or protect someone's safety
- Enforce our Terms

If we're ever acquired or merged, your data may transfer with the business. We'll tell you first, and this policy keeps applying until it's replaced by one you're told about.

## 5. How We Protect It

### 5.1 What We Actually Do
- Encryption in transit (TLS) and at rest
- Field-level encryption for bank details, tax IDs and integration tokens
- Passwords stored as salted hashes, never in readable form
- Every carrier's data isolated at the database layer, enforced on every query
- Role-based access, and audit trails on sensitive actions
- Internal security review before releases, and prompt patching of dependencies

We'd rather be straight with you than impressive: we do not currently hold SOC 2 certification or a third-party penetration test report. When that changes, this section will say so.

### 5.2 If Something Goes Wrong
- We investigate immediately
- We notify affected accounts within 72 hours of confirming a breach
- We tell you what happened, what was exposed and what we're doing — without spin

## Google API Services User Data Policy Compliance

Octopus TMS's use and transfer to any other app of information received from Google APIs will adhere to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.

When you connect your Google account to Octopus TMS, we access your Google account data solely to provide the user-facing features you have explicitly requested — specifically, sending emails on your behalf from your Gmail account to brokers, carriers, and drivers in connection with load operations.

We commit to the following:

- **Limited use.** We use Google user data only to provide and improve the specific user-facing features you have authorized.
- **No advertising.** We do not transfer, sell, or use Google user data for serving advertisements, retargeting, or any personalized or interest-based advertising.
- **No lending decisions.** We do not use Google user data to determine credit-worthiness or for lending purposes.
- **No AI/ML training.** We do **not** use Google user data to develop, improve, or train generalized or non-personalized artificial intelligence (AI) or machine learning (ML) models. We do not retain Google user data for any AI/ML training purpose.
- **No human access**, except: (a) with your specific affirmative consent for particular messages, (b) for security purposes such as investigating a bug or abuse, (c) to comply with applicable law, or (d) where the data is aggregated and anonymized and used solely for internal operations.
- **Token storage.** OAuth access and refresh tokens are encrypted at rest using AES-256-GCM and are accessible only to the authenticated user's Octopus TMS account.
- **Disconnection.** You may disconnect your Google account at any time from Settings → Integrations. On disconnect we revoke the tokens with Google and delete them from our systems.

## 6. Your Rights

### 6.1 What You Can Ask For
- A copy of the personal data we hold about you
- Correction of anything inaccurate
- Deletion of your account and its data, subject to the retention rules below
- An export of your data in a machine-readable format, any time

Email private@thedigitalronin.com and we'll respond within 30 days. We won't charge you, and we won't treat you differently for asking.

### 6.2 Communication Preferences
- You can opt out of non-essential notifications any time
- Transactional messages — load assignments, payment and security alerts — can't be turned off while your account is active. They're how the platform works

## 7. How Long We Keep It

| Data | Retention |
|------|-----------|
| Account and operational data | For as long as your account is active |
| Financial records — invoices, settlements, tax documents | 7 years, as tax and DOT rules require |
| **Trip location history — raw GPS breadcrumbs** | **5 years** from the date of the trip, then deleted. Deletion runs monthly, so records may remain up to one month longer |
| Route summary and stop times attached to a completed load | 7 years, with the load record |
| Messages and notification logs | 3 years |
| Technical and security logs | 90 days |
| Closed account | Exportable for 60 days, then deleted except records we must keep by law |

If data is subject to a legal hold, we keep the affected records until the hold is lifted.

**Why trip location is kept for 5 years.** Freight disputes surface long after the truck has moved: cargo claims run about three years, accident records must be kept three years by federal rule, and injury and contract claims run two to four years in most states. Five years covers those windows and mirrors the period the DOT already sets for other driver records. It is a limit, not a default — nothing is kept indefinitely, and off-duty location is never collected in the first place.

## 8. Where Your Data Lives

Your data is stored and processed in the United States. If you access the platform from elsewhere, you're sending it to the US. Where the law requires safeguards for those transfers, we put them in place.

## 9. California Privacy Rights (CCPA/CPRA)

If you're a California resident, you have the right to know what we collect, to correct it, to delete it, to receive a portable copy, to limit our use of sensitive personal information, and not to be discriminated against for exercising any of those rights.

**We do not sell or share personal information** as those terms are defined by the CCPA/CPRA, and we have not in the past 12 months. There is nothing for you to opt out of.

**Sensitive personal information:** precise geolocation, financial account numbers and government identifiers. We use them to deliver the Service you asked for and to defend claims arising from it — never to infer characteristics about anyone, and never for profiling or advertising. Those are permitted purposes under CPRA, so no separate limit-the-use request is needed. You can still make one.

**Drivers.** If you drive for a carrier that uses Octopus, that carrier decides that you are tracked and for which loads; we process trip location on their instructions as a service provider. You hold the same rights listed above and can exercise them with us directly at the address below, and your carrier may owe you separate written notice of monitoring under your state's law.

To exercise any right, email private@thedigitalronin.com. An authorized agent may act for you with written permission.

## 10. Children's Privacy

This is a commercial trucking platform. It isn't for anyone under 18, and we don't knowingly collect data from children. If we learn we have, we delete it.

## 11. Updates to This Policy

We update this policy when the platform changes — a new integration, a new data type, a new retention rule. Material changes get 30 days' notice by email and in-app. The effective date at the top always tells you which version you're reading.

## 12. Contact Us

Privacy questions, data requests, or anything in this policy that reads wrong to you:

**Octopus TMS**
Operated by Digital Ronin LLC
Email: private@thedigitalronin.com
Phone: +1 (412)510-5854

## 13. Cookies

We use cookies and local storage to keep you logged in, remember your preferences such as language and theme, and understand which features get used so we know what to improve.

No advertising cookies. No third-party tracking pixels. Blocking cookies in your browser will break login.

---

By using Octopus TMS, you acknowledge that you've read and understood this Privacy Policy.

## 14. Version History

- **2.1** — August 28, 2026: Added Data Processing Addendum cross-reference and version history. Acceptance is now recorded per user, document version, and timestamp at signup.
- **2.0** — August 2026: Full rewrite against the real product.
- **1.0** — December 2024: Initial version.
