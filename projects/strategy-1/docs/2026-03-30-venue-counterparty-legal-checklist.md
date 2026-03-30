# Strategy #1 Venue and Counterparty Legal Checklist
Date: 2026-03-30

## Executive Summary
This checklist defines legal and contractual controls required before Team GSD connects Strategy #1 to any exchange, broker, liquidity venue, market-data source, or infrastructure provider. The objective is to avoid contract breaches, prohibited trading conduct, account-control violations, and data-rights misuse. Each venue or counterparty should be approved only after checklist completion and legal signoff. Any unresolved High-risk item is a block for production use.

## Jurisdiction(s) Affected
- United States (federal and state legal/regulatory perimeter)
- Governing-law and dispute venues defined in each contract/terms of service
- Additional local laws in any jurisdiction where venue access or counterparties are located

## Risk Rating
High

## Recommended Next Action
Run this checklist for every proposed venue and counterparty and complete initial approvals for launch candidates by **2026-04-05**.

## Checklist
### 1. Entity and Account Authority
- [ ] Account owner legal entity is documented and approved
- [ ] Authorized traders/service accounts are named with role-based access limits
- [ ] Account-sharing, sub-account, and delegation rules are reviewed
- [ ] Beneficial ownership and control representations are accurate and supportable

### 2. Jurisdiction and Eligibility
- [ ] Venue permits use by Team GSD entity and operating jurisdiction(s)
- [ ] Restricted-country and sanctions controls are compatible with onboarding model
- [ ] Product-level restrictions (spot/derivatives/margin/lending) are mapped
- [ ] Local regulatory restrictions for contemplated activity are documented

### 3. Terms of Service and Conduct Restrictions
- [ ] Prohibited trading practices are extracted and mapped to strategy behavior
- [ ] API automation limits and anti-abuse clauses are reviewed
- [ ] Order placement/cancellation constraints are reviewed against execution logic
- [ ] Suspension/termination rights and clawback provisions are documented

### 4. Data and IP Rights
- [ ] Market-data rights are mapped: internal use, display, derived data, redistribution
- [ ] API/data scraping restrictions and reverse-engineering clauses are reviewed
- [ ] Audit rights, reporting duties, and data-entitlement verification are understood
- [ ] IP ownership and license terms for vendor SDKs/tools are approved

### 5. Custody, Collateral, and Asset Handling
- [ ] Custody model (segregated/omnibus/self-custody interfaces) is documented
- [ ] Rehypothecation, lien, and setoff rights are reviewed
- [ ] Withdrawal controls, settlement timing, and holdback rights are understood
- [ ] Incident and insolvency treatment language is reviewed

### 6. Liability, Indemnity, and Dispute Process
- [ ] Liability caps, exclusions, and force majeure language are reviewed
- [ ] Indemnity obligations are accepted by legal and business owner
- [ ] Governing law/arbitration/forum selection is documented
- [ ] Evidence retention obligations for disputes are integrated into logging controls

### 7. Security, Privacy, and Operational Controls
- [ ] Security obligations for API keys, credentials, and incident notice are documented
- [ ] Privacy/data transfer terms for logs and telemetry are reviewed
- [ ] Required audit logs are mapped to engineering controls
- [ ] Vendor SOC/assurance artifacts are collected where required

### 8. Approval and Ongoing Monitoring
- [ ] Legal signoff recorded
- [ ] Engineering signoff recorded
- [ ] CEO/operating owner signoff recorded
- [ ] Review cadence set (minimum quarterly or on material terms change)
- [ ] Trigger conditions defined for re-review (new products, new jurisdictions, new data use)

## Evidence to Archive Per Venue/Counterparty
- Executed terms or latest accepted terms snapshot
- Summary of prohibited practices and strategy compatibility decision
- Data-rights matrix entry
- Risk exceptions (if any) and approving authority
- Date of next required review
