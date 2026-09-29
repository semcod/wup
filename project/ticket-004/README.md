# ticket-004: Dedupe WUP incident tickets by failure signature

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: the user requested continuation of autonomous
maintenance work; this ticket fixes the observed duplicate incident flood.

AC-01: While any ticket for the same `(service, stage, status)` signature is
open, a new failure event mutes instead of creating a sibling ticket — even
when the failure message (and therefore the exact fingerprint) differs.

AC-02: After the signature ticket reaches a terminal status, re-filing is
suppressed for `planfile.refile_cooldown_seconds` (default 24h), measured from
the ticket's `updated_at` or the first observed close time, so a chronically
flapping probe does not produce a new ticket per event.

AC-03: A signature whose last ticket closed longer ago than the cooldown files
a fresh ticket, preserving regression visibility.

AC-04: Lookup failures remain conservative: an unreadable ticket is treated as
open and keeps muting.

Evidence: `maskservice/c2004/.wup/planfile-tickets.json` holds 136 fingerprints
including 43 distinct tickets for `connect-scenario/probe-latency/degraded`
alone.
