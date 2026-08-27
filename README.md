a# SE Lab 1: Requirements Engineering and UML Use-Case Modelling

**R Saurav Srrinivas**
**SRN: PES1UG24CS352**
PES University, Department of Computer Science and Engineering

**Problem Statement 44: Database Query Performance Profiler**

A database observability tool that collects slow query logs, parses execution plans, works out which indexes are missing, and sends a weekly optimization digest.

## Files

| File | What it is |
|---|---|
| `PES1UG24CS352_Lab1_Requirements_Table.pdf` / `.docx` | Deliverable 1: five FRs and two NFRs with ID, type, description, priority, acceptance criteria, rationale and a blank comments column |
| `PES1UG24CS352_Lab1_UseCase_Diagram.pdf` | Deliverable 2: the use-case diagram |
| `PES1UG24CS352_Lab1_UseCase_Diagram.drawio` | Editable diagram source. Open it at app.diagrams.net through File > Open From > Device |
| `PES1UG24CS352_Lab1_UseCase_Flow.pdf` / `.docx` | Deliverable 3: one page flow for UC-03 with preconditions, postconditions, main scenario and two alternate flows |
| `PES1UG24CS352_Lab1_All_Deliverables.pdf` | All three deliverables in a single PDF |

## Actors

| Actor | Type | What they do |
|---|---|---|
| Database Administrator | Primary | Adds databases, sets the profiling options, reviews and triages the index suggestions |
| Backend Lead | Primary | Reads the weekly digest and decides which suggestions to take |
| Monitored Database Server (Postgres / MySQL) | Supporting | Where the slow query logs, EXPLAIN plans and catalog statistics come from |
| Report Scheduler | Supporting | Kicks off the weekly digest job |
| Notification Service (Email / Slack) | Supporting | Sends the digest out |

## Use cases

| ID | Use case | Comes from |
|---|---|---|
| UC-01 | Ingest Slow Query Logs | FR-002, NFR-001 |
| UC-02 | Analyse SQL Execution Plan | FR-001 |
| UC-03 | Recommend Index Candidates | FR-001, FR-005 |
| UC-04 | Generate Weekly Digest | FR-004 |
| UC-05 | Configure Profiling Settings | FR-003, NFR-002 |
| UC-06 | Fingerprint and Deduplicate Query | FR-002 |
| UC-07 | Simulate Index on Replica | FR-005 |
| UC-08 | Export Digest as PDF/CSV | FR-004 |

Include and extend relationships used in the diagram:

- UC-01 includes UC-06, because every collection run has to fingerprint the statement before storing it.
- UC-03 includes UC-02, because you cannot suggest an index without first reading the plan.
- UC-04 includes UC-03, because the digest regenerates the suggestion list each week.
- UC-07 extends UC-03, since trying the index on a replica is optional.
- UC-08 extends UC-04, since exporting the digest is optional.

## Note

The comments column in the requirements table is deliberately left blank. It gets filled in during the peer review step of the lab, after which the table is revised.
