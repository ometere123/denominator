# Threat model

## Assets and scope

Integrity of the declared cohort snapshot; preservation of every census member through reporting; honest case classification; exact vs bounded rate distinction; consumer definition hash. Denominator does not hold funds.

## Attacker goals and mechanisms

| Attack | Defense | Remaining limitation |
| --- | --- | --- |
| Cherry-pick 19 successful IDs from 100-member published census | The contract independently fetches the **entire** frozen manifest and creates each member, not a caller's chosen subset | A malicious original index publisher could omit 80 members **before closure**; the result is always scoped to the declared index |
| Modify census after observed failures | Re-fetch at finalization; changed canonical list invalidates certificate | Mutable hosts can disappear indefinitely, blocking finalization |
| Pretend 404/missing case is a failure or exclusion | `UNAVAILABLE` blocks certificate; only direct affirmative excerpts can justify exclusion/failure | No independent guarantee of source completeness |
| Leave pending cases out of denominator | `UNKNOWN` is included in denominator; output is bounds, not exact percentage | Missing eligibility evidence remains `AMBIGUOUS` and prevents any certificate |
| Forge leader class | Validator independently re-fetches, re-classifies, checks case ID and source digest | Correlated model failures remain possible |
| Fabricate quotation | Contiguous source inclusion check and independently adjudicated alternative excerpt | Source itself may contain false statements |
| Prompt injection via page text | Source and rules explicitly inert in prompt, bounded output and independent verification | Not a formal proof of prompt-injection immunity |
| Dynamic page diverges across validators | Source digest agreement; fail closed on drift | Can affect liveness; stable immutable source URLs preferred |
| SSRF and local metadata | HTTPS-only restricted host syntax, block literal IP and recognized private names | DNS-rebinding/CDN aliases require network-level protections from the runtime |
| Hide denominator by inventing zero population | Zero-eligible terminal state has no rate certificate | Proper eligibility requires an independently inspectable rubric and public source |
| Replay old certificate for new period | Expected definition hash includes cohort digest and time window | Integrator must actually pin the expected hash |
| Attack via open observation calls | Only indexed cases, max three retries for uncertain states, definitive case status immutable | Permissionless calls still require transaction fees; operator should monitor spam |
| Suppress finalization | Any caller can finalize after deadline, with immutable census | Source unavailability can prevent the consensus check |
| Claim certified rate with rounding errors | Integer floor/ceiling basis-point boundaries | Tiny sub-bps differences intentionally not represented |

## Explicit non-goals

No universal authority discovery, no off-chain private records, no general proof that an omitted event does not exist, no proof that a publicly listed case is authentic, no hidden identity inference, no automatic payouts or trustless custody, no web UI, no direct controller over an external service.

## Safety invariants

1. Every member in the sealed index remains in on-chain `case_ids` and is accounted for at finalization.
2. No excluded case without positive evidence excerpt.
3. No source-unavailable case becomes a recorded failure.
4. No exact certificate when any in-scope outcome remains unknown or any census member remains unresolved.
5. No consumer acceptance when the expected `definition_hash` differs.
6. No certified result after census drift.
7. No model-directed arithmetic, member creation, token transfers or cross-contract calls.
8. No observations before prospective start or after observation deadline.

## Acceptance-bar exceptions

If real StudioNet validators do not agree on structurally equivalent JSON or bounded classifications from immutable public fixture pages, record that as a blocker. Never report a mere FINALIZED transaction with execution ERROR as success. If test harness or GenVM artifact is unavailable, record the environment limitation rather than fabricating a pass.
