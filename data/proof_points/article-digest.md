# Article Digest -- Proof Points

Compact proof points from portfolio projects and work stories. Read by career-ops at evaluation time.

---

## ESA Microsoft 365 Copilot Adoption Program

**Hero metrics:** 1,896 licensed users (90% over the 1,000-user target), 47% growth in active users (1,075→1,578), 83% utilization

**Context:** Utilization was tracking below the program's target despite full licensing rollout. Rather than relying on secondhand reporting, attended live adoption-coaching sessions directly to observe what users were asking and what coaches were advising, in order to diagnose the actual gap.

**Key decisions:**
- Diagnosed that most recurring user questions centered on security and data-classification concerns — specifically, confusion over the maximum permitted document security/protection level (PL) for Copilot use, given ESA's multi-tier confidentiality framework.
- Partnered with the Security and DPO (Data Protection Officer) teams to clarify and raise the permitted security level for Copilot-eligible documents.
- Redesigned the coaching curriculum to add a dedicated segment on security and protected-document (PL) handling for Copilot, closing the specific gap identified in the field.

**Proof points:**
- Adoption metrics improved following the security clarification and curriculum change: 1,896 licensed users, 47% adoption growth, 83% utilization (see `cv.md` Key Achievements).
- Demonstrates root-cause diagnosis (attending sessions directly rather than trusting reports) and cross-functional problem-solving (security/DPO partnership) behind an adoption metric.

---

## ESA Azure Cost-Center Billing Pipeline

**Hero metrics:** First-ever pay-as-you-go Azure billing to end users at ESA; replaced a fully fixed-monthly-rate IT billing model; built as an extensible system for adding new billable services

**Context:** All ESA IT services had historically been billed at a fixed monthly rate — there was no mechanism to bill dynamic, consumption-based cloud services. When ESA needed to start billing Azure pay-as-you-go usage directly to end users, no link existed between the internal IT service-request system (Helix) and Azure's own cost-center data, so there was no way to attribute Azure spend back to the request that generated it.

**Key decisions:**
- Fetched Azure cost-center data via API rather than manual export, to make the pipeline repeatable/automatable.
- Modified Azure resource tagging to embed the corresponding Helix service-request ID directly on the Azure service/resource — creating a durable, queryable link between an internal service request and its Azure cost record.
- Cleaned and processed the raw Azure cost data, then joined it against Helix records using the tag-based relation to attribute cost to the correct requester/cost center.
- Delivered the processed, request-attributed cost data to the finance team so they could bill end users directly, rather than finance reconciling spend manually.
- Designed the pipeline to be extensible so new Azure services could be onboarded into the billing flow without rearchitecting it.

**Proof points:**
- Enabled ESA's first pay-as-you-go Azure billing to end users — previously impossible under the fixed-rate model.
- Went from "no link between IT requests and cloud cost" to a working, tag-based attribution system built end-to-end solo (API ingestion → tagging change → data processing/merge → finance delivery).
- Extensible-by-design: built to onboard future Azure services without a rebuild (see `cv.md` Key Achievements: "data warehouse solution, implementing API-driven data ingestion and automated scheduling for Azure billing data delivery to finance").

---

<!-- Add more entries below as they come: job-analyser/enterprise-ai-evaluator project deep-dives, articles, talks. Same format: Hero metrics, Context, Key decisions, Proof points. -->
