# Driver discovery — issue #231 field kit

Prepared 2026-09-28 by Codex Forge on the PC. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.

**State: preparation only. No drivers recruited, estimates delivered, observation windows started, or teacher approvals recorded in this pack.**

Authority: [issue #231](https://github.com/RobynAwesome/Introduction-to-MCP/issues/231), read live on 2026-09-28. The issue remains open; its field completion checkboxes remain unfulfilled. This pack supplies working materials for those existing tasks, not a second experiment or a new protocol.

## Why this test exists

Robyn reports more than 15 driver conversations, expressed interest, and no driver-initiated follow-up that became a lead. This is direct testimony as recorded in the issue, not a measured cohort. Exact dates, denominator and driver-level records have not been provided. This PC task received the pasted handoff and live issue; it has not inspected the full original DH conversation.

The analytical question is the gap between expressed interest and a later voluntary action. Possible explanations include usefulness, timing, trust, effort, channel, and control of vehicle/fuel costs. These are competing hypotheses, not conclusions about Robyn or drivers.

Test whether a private, checkable estimate gives a driver a reason to contact Robyn again. A response cannot validate a dispatcher, risk map, demand forecast, revenue, savings or buyer identity.

## Mobile and PC responsibilities

| Lane | Work and boundary |
|---|---|
| Robyn on mobile | Choose whom to invite, obtain consent, send and receive WhatsApp messages, correct facts and control participation. |
| Forge on PC / MAO preparation | Prepare materials, calculate only from supplied inputs, preserve minimal private records and make uncertainty visible. No messaging automation. |
| MMAO / cloud continuity | Issue #231 supplies the shared bounded brief. This public preparation packet contains instructions only; a later minimized outcome receipt can return evidence to that lane. |
| KC | Keep testimony, hypotheses, source evidence and field outcomes distinct. No KC runtime invocation is claimed. |
| Cassey | Separate review of wording, calculation and interpretation after actual field receipts exist. The attached handoff is prepared, not sent or approved. |

Canonical role history is preserved; these are responsibilities for this issue, not new acronym definitions, seat appointments or claims of activation.

## Operator sequence

1. Invite individuals privately. Record every invitation and its outcome using a pseudonymous ID; do not enter names or numbers in these files. Admit no more than five consenting drivers. A decline is not a consent, and a withdrawal is not a slot to replace selectively.
2. On YES, send the data-use note below and wait for agreement before putting shift inputs into the separate ledger. A driver may skip the optional role/ownership/fuel-payer question.
3. Ask for empty kilometres, fuel price in rand per litre, and consumption with its unit. Never assume a typical car, price, commission or route.
4. Return the labelled calculation. Record submission time, receipt version, sent time and confirmed delivery time. UNKNOWN is not a completed estimate.
5. Observe each recipient for 168 hours from the first delivered checkable estimate. Record inbound events and any operator messages. Do not solicit a return, send a reminder, or request feedback during that window. Respond to questions and necessary corrections, and log their origin.
6. At the end of the window, classify the observed events and incomplete cases. Seek an explanation only afterwards and only if the driver agrees. Preserve volunteered reasons as testimony.
7. Assemble the minimized review packet in TEACHER-REVIEW.md. Review the evidence before TEST_AGAIN / PIVOT / HOLD. Nothing in this pack automatically closes the issue.

Recruitment can be staggered. Seven full observation days are required for each recipient; this is not necessarily seven calendar days from the first invitation to the final outcome.

## Messages for Robyn to send manually

### Invitation — wording from issue #231

> I’m testing a free shift check. After a shift, send the kilometres you drove empty and your own fuel price plus car consumption estimate. I’ll reply with the estimated fuel cost of those empty kilometres. No live tracking or location needed. Want to try it once? Reply YES. You can stop anytime.

### Data-use note — proposed addition, before separate logging

> I’ll keep a short private record of your figures, my calculation, corrections and whether you contact me again during the next seven days. It will use a code instead of your name or number. I may share a summary of counts for review, without your chat or identifying details. You can say STOP to leave or DELETE to ask me to remove my separate test notes. I’ll remove those notes within 14 days after your seven-day observation window ends, or within 14 days after you stop if it ends earlier. This does not control WhatsApp’s own records or backups. Is that okay?

The retention limit is an operational proposal in this pack. Robyn must perform and log deletion; no deletion scheduler exists. If different terms are agreed, record the exact consent version before collecting data. A deletion request must be handled promptly; do not wait for the routine deadline. For a consenting driver who never receives a qualifying estimate, end intake no later than seven days after consent and delete the separate notes within the following 14 days. Do not retain identifiable withdrawal or deletion records against the driver’s request; aggregate reporting must remain within consent.

### Input request

> For the shift you want checked, please send: (1) kilometres driven empty, (2) the fuel price you used in rand per litre, and (3) your car’s consumption estimate, including whether it is km per litre or litres per 100 km. Please don’t send your live location, passenger details or group chats. If you don’t know a figure, say “don’t know”.

### Optional context

> Optional: do you own or rent the car, and who pays for fuel? You can skip this.

### Estimate reply

> Your estimated fuel cost for those empty kilometres is **R[amount]**. You supplied [empty_km] km empty, [km_per_litre] km/L and R[rand_per_litre]/L. Calculation: [empty_km] ÷ [km_per_litre] × [rand_per_litre] = R[amount]. This is an estimate from your figures, not measured savings or a route recommendation. It excludes other vehicle costs and fuel use not represented by those inputs. You can correct any figure or ask me to stop.

If the driver supplied L/100 km, show that original unit and the calculation `empty_km × litres_per_100km ÷ 100 × rand_per_litre`; optionally show `km_per_litre = 100 ÷ litres_per_100km`. Do not put an L/100 km value into the km/L formula.

### Missing or invalid input

> I can’t calculate a checkable estimate yet because [specific figure or unit] is missing or unclear. Please confirm it if you know it. I won’t substitute a typical value.

### Correction

> Correction to estimate [receipt ID]: [old figure/calculation] should be [corrected figure/calculation]. The revised estimate is R[amount]. [Brief reason.] The first version was an estimate and is now superseded.

Append a linked revision while retention is permitted; never quietly overwrite the earlier calculation. A correction does not restart the seven-day clock. Record whether the initial receipt was invalid due to operator error; disclose affected outcomes separately.

## Calculation checks

The input must be numeric, finite, non-negative for empty kilometres and fuel price, and strictly positive for consumption. Zero empty kilometres is valid. Confirm a supplied zero fuel price rather than rejecting or replacing it. Reject negative, missing, infinite or ambiguous values. Agree what the driver counted as empty kilometres; do not infer it from location.

Round the final rand amount to two decimals, not the intermediate consumption conversion. Input quality and real consumption remain unverified even when the arithmetic is correct.

Synthetic arithmetic examples only — none are driver receipts or recommended fuel prices:

| Empty km | Driver-style input | Fuel input | Expected estimate |
|---:|---|---:|---:|
| 48 | 12 km/L | R23.50/L | R94.00 |
| 48 | 8.333333333333333 L/100 km | R23.50/L | R94.00 after final rounding |
| 0 | 12 km/L | R23.50/L | R0.00 |
| 48 | missing or 0 km/L | R23.50/L | UNKNOWN; no receipt denominator entry |

## Outcome definitions — freeze before recruitment

These are transparent working clarifications for the issue, not canonical protocol changes. Preserve both the issue wording and event-level evidence so a reviewer can challenge them.

- **First receipt:** a delivered, checkable estimate with all three driver-supplied inputs and explicit units. A sent-but-unconfirmed message is delivery unknown; a WhatsApp delivery marker proves delivery, not reading. A driver need not praise the estimate to enter the denominator.
- **Window:** strictly after first delivery and up to and including 168 hours later. Record timezone offsets, normally +02:00. Do not move the start to obtain a favorable result.
- **Primary issue denominator:** all drivers confirmed to have received their first qualifying receipt. Preserve this historical count when reporting incomplete observation, subject to consent and deletion. Never count unknown delivery as confirmed receipt.
- **Contact events:** record all subsequent driver contacts with timestamps and categories: acknowledgement, correction, new shift request, general question, opt-out, other. Keep same-exchange versus later-exchange context. Categories are local log labels, not new estate protocols.
- **Literal count and repeat-use count:** report confirmed independently initiated subsequent contact separately from an independently initiated request for another shift check. A thanks, correction or STOP is not evidence of repeat utility. Each driver contributes at most one to each count.
- **Independence:** mark yes, no or uncertain, with a reason and the preceding operator-contact reference. A response to outreach is prompted. Do not use an arbitrary silence period as proof of independence. An immediate continuation with unclear meaning stays uncertain rather than being promoted to a success.
- **Observation state:** complete, pending, withdrawn, deleted or unobservable, reported separately. Only a complete observable window with no qualifying contact can be a completed zero. Missing data cannot be filled with zero.
- **Counting:** report `confirmed independent second contacts / all first-receipt recipients`, plus all unresolved states and contact categories. Also report independent new-shift requests with the same denominator. If the denominator is zero, the ratio is undefined, not 0% retention.
- **Issue threshold:** two or more independent second contacts in a five-recipient test warrants consideration of another bounded test, not a product claim. Apply no equivalent threshold to a smaller or unresolved cohort. Contacts consisting only of complaints or withdrawals require interpretation; the threshold is not automatic permission to automate.

Example: one observed independent contact among five receipt recipients with two windows still open is `1/5 observed, 2 pending`. It is not a completed conversion finding. Five completed windows with zero contacts establishes only no observed return under this offer and these conditions; it does not establish why.

## Private ledger and handoff

The CSV files under `private-ledger/` start with headers only. Do not pre-fill synthetic participants. Keep all completed files outside public repositories and cloud issue comments. No phone numbers, full chats, raw voice notes, third-party names or precise locations belong here. A pseudonym does not make data anonymous or prove legal compliance.

- `participants.csv`: invitations, consent, voluntary context, first receipt, window and deletion handling.
- `estimates.csv`: supplied input values and units, calculations, sent/delivery times and linked corrections.
- `contacts.csv`: driver and operator events, prompts, contact types and minimal consented reasons.

Use the ordinary private WhatsApp conversation as the source if permitted; a local receipt reference should be an opaque ID, not a phone number or copied transcript. Record response time as estimate sent time minus complete-input submission time; distinguish it from delivery delay. Do not paste personal identifiers into an AI chat to get the arithmetic done.

Current summary: invitations recorded = 0; consenting participants recorded = 0; first receipts delivered = 0; observation windows started = 0. All experiment outcomes remain unknown. These zeros describe this newly created pack only, not Robyn’s historical conversations.

Review handoff: [TEACHER-REVIEW.md](TEACHER-REVIEW.md). Provenance: [PREPARATION-RECEIPT.md](PREPARATION-RECEIPT.md). Peer method review: [PEER-REVIEW.md](PEER-REVIEW.md).
