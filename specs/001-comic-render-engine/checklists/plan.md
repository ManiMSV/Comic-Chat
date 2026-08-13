# Plan/Design Quality Checklist: Comic Render Engine

**Purpose**: Validate the quality, clarity, completeness, and consistency of the plan, research, data-model, and API-contract requirements before implementation
**Created**: 2026-08-11
**Resolved**: 2026-08-13 — all 35 items verified against the amended docs; gaps fixed in spec/plan/research/data-model/tasks (CHK006, CHK010, CHK015, CHK016, CHK020, CHK022, CHK030)
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md) · [data-model.md](../data-model.md) · [contracts/api.md](../contracts/api.md)

## Requirement Completeness

- [X] CHK001 Is a determinism requirement (pure function, no wall-clock/random/LLM dependence) stated for *every* derived decision (expression, balloon, placement, layout), not just generically? [Completeness, Spec §SC-002, Plan §Constraints] — Determinism is pinned per decision: emotion/expression (research §1), balloon (research §4, data-model §Message), placement (research §6), panel layout (research §5), plus the deterministic message `id` (data-model §Message). Constitution II and plan §Constraints require it globally.
- [X] CHK002 Are derivation-rule requirements specified for each of the five emotions and all three balloon shapes? [Completeness, Spec §FR-003/§FR-004, Data §Message] — All five emotions with word sets + precedence (research §1); all three balloon shapes with precedence (research §4, data-model §Message).
- [X] CHK003 Is the panel-splitting behavior fully specified for all message-count ranges (1–4 single panel, 5–8 split, >8 multi-panel)? [Completeness, Spec §FR-006, Data §Validation] — Capacity 4 + turn-change split + cap-at-4 (research §5, data-model §Panel); ranges 1–4 and 5–8 explicit in the matrix; >8 composes the same rule in reading order.
- [X] CHK004 Are requirements defined for the typo/length bounds of input (`text` max 500, min-1 messages, trimmed non-empty)? [Completeness, Data §Message, API §Request] — `text` max 500, trimmed non-empty; `messages` min 1 (data-model §Message/§Validation, contracts/api.md §Request).
- [X] CHK005 Are requirements defined for identifying which characters appear in a panel versus the full v1 cast in the response? [Completeness, Data §Panel/§Comic] — `Panel.characters` lists only the panel's speakers as `CharacterPlacement`; `ComicInstruction.characters` carries the cast (data-model §Panel/§Comic, contracts §Types).

## Requirement Clarity

- [X] CHK006 Is the shouting threshold ("≥50% uppercase AND ≥3 alphabetic chars") unambiguously defined (what counts as an alphabetic char; how Unicode/non-ASCII is treated)? [Clarity, Data §Message, Research §2] — Amended research §2: alphabetic = `str.isalpha()` (Unicode letters); digits/punctuation ignored; zero-alphabetic never shout; worked examples included.
- [X] CHK007 Is the `[thought]` marker's detection precisely defined (leading marker only, case-sensitivity, trimming before detection)? [Clarity, Data §Message, Research §3] — Leading marker on trimmed text, case-insensitive, stripped from display (research §3, data-model §Message, spec §US3).
- [X] CHK008 Is the emotion keyword/stemset matching rules specified (substring vs. word-boundary vs. stem match)? [Clarity, Data §Message, Research §1] — Whole-word boundary on lowercased text against the enumerated authoritative sets (research §1); `yay` ≠ `yesterday`.
- [X] CHK009 Is "turn parity + speaker identity" placement specified precisely enough to be implementable (what determines the initial left/right assignment)? [Clarity, Data §Panel, Research §6] — Initial side = order of first appearance; side maps globally to identity and is stable across panels (research §6, data-model §Panel).
- [X] CHK010 Are the three demo dialogues' content/IDs/order specified, not just the count? [Clarity, Spec §FR-011, API §Demos] — Amended data-model §Demo Dialogues pins order, `id`, `name`, message bodies, and balloon/emotion coverage for all three; tasks T012 references it.

## Requirement Consistency

- [X] CHK011 Does the emotion precedence order match everywhere it appears (Spec §FR-10, Research §1, Data §Message, API §Types)? [Consistency] — `anger > surprise > joy > sadness > neutral` identical in spec, research §1, data-model §Message, and contracts §Types.
- [X] CHK012 Is the balloon-shape precedence (shout → thought → speech) consistent across Spec, Research §4, Data §Message, and API §Types? [Consistency] — Same precedence in all four docs.
- [X] CHK013 Do panel-split rules (max 4, turn-change boundary) align between Spec §FR-006, Research §5, and Data §Panel? [Consistency] — Max 4 + turn-change boundary + cap aligned across all three.
- [X] CHK014 Is the error contract mutually consistent (422 conditions identical in Data §Validation and API §Errors)? [Consistency] — Empty/absent messages, empty/whitespace text, unknown speaker_id, overlong text → 422 in both docs.
- [X] CHK015 Does the frontend sidebar/nav copy removal of Items CRUD align with the backend removal in Plan §Structure? [Consistency, Spec §Assumptions] — Amended plan §Structure + tasks T001 to explicitly remove the `AppSidebar.tsx` Items nav entry; aligns with backend route/model deletion.

## Acceptance Criteria Quality

- [X] CHK016 Can SC-003 ("first attempt success") be objectively verified given undefined expected render for each demo? [Measurability, Spec §SC-003] — Amended data-model §Demo Dialogues defines each demo's expected expression/balloon coverage, making SC-003 objectively checkable.
- [X] CHK017 Is SC-002 (100% reproducibility) framed with an unambiguous definition of "same layout and expressions" (exact-enum comparison vs. rendered pixels)? [Measurability, Spec §SC-002] — Deterministic message `id` (hash of speaker_id+text+index) makes the response byte-identical; T009 asserts two responses byte-identical.
- [X] CHK018 Are objective, testable acceptance criteria or derivation-unit expectations defined for each edge case (conflicting emotions, all-caps+long, overflow, cross-panel speaker)? [Acceptance Criteria, Spec §Edge Cases] — Each edge has a documented derivation rule (precedence, shout+wrap, split, stable side) and SC-004 mandates automated tests (T019–T025).

## Scenario Coverage

- [X] CHK019 Is the primary two-character alternating render scenario covered end-to-end? [Coverage, Spec §US1] — US1 acceptance 1 + independent test + T018 E2E covers an alternating two-speaker dialogue.
- [X] CHK020 Are alternate scenarios covered (3+ characters, single message, single speaker repeated)? [Coverage, Gap present? Data §Validation] — 3-char cast is defined; 3+ speakers in one panel is two-character-by-construction (research §6). Single message in matrix; single-speaker-repeated row added to the matrix (data-model §Validation).
- [X] CHK021 Are exception flows fully specified (unknown speaker_id, empty conversation, overlong text) with defined responses? [Coverage, Data §Validation] — All three → 422 with clear message (data-model §Validation, contracts §Errors).
- [X] CHK022 Are recovery/empty states defined client-side (loading/empty/error while fetching demos or rendering)? [Coverage, Gap] — Amended plan.md §Frontend UX & Accessibility defines loading, empty (no render yet), error/retry states; wired into T017.

## Edge Case Coverage

- [X] CHK023 Is the conflicting-emotion outcome deterministically specified via the precedence order? [Edge Case, Spec §Edge Cases, Research §1] — Yes: fixed precedence resolves any conflict deterministically.
- [X] CHK024 Is the multi-panel "speaks last in panel N / first in panel N+1" side-stability requirement specified? [Edge Case, Spec §Edge Cases, Research §6] — Global identity→side mapping keeps placement stable across panels (research §6).
- [X] CHK025 Is all-caps-plus-long-text wrapping specified (balloon wraps within panel regardless of length)? [Edge Case, Spec §Edge Cases, Research §2] — Explicit in research §2 and the spec edge case.
- [X] CHK026 Is the boundary case of exactly 4 messages (no split) vs. exactly 5 (must split) specified? [Edge Case, Data §Validation] — Matrix: 1–4 single panel; 5–8 split; split falls at latest turn change ≤4 else cap.
- [X] CHK027 Is behavior specified for non-two-character output (v1 is two-character by construction) if the demo cast allows 3? [Edge Case, Gap/Assumption] — Panels are two-character by construction (research §6); the 3-character cast is documented; a 3+ speaker panel is explicitly excluded in v1.

## Non-Functional Requirements

- [X] CHK028 Are the performance target ("<10s") and determinism non-functional requirements quantified and testable? [NFR, Spec §SC-001/§SC-002] — SC-001 "<10 s"; SC-002 byte-reproducibility; both verifiable (T009 determinism; quickstart matrix for SC-001).
- [X] CHK029 Is a usability requirement specified for the demo "render with one action" (FR-011) measured objectively? [NFR, Spec §FR-011] — FR-011 one-action demo; verifiable via demo picker (T017) + E2E (T018) and SC-003.
- [X] CHK030 Are accessibility requirements specified for the comic SVG markup (e.g., text alternatives, keying) for a comic deliverable? [NFR, Gap] — Amended spec §Assumptions + plan.md §Frontend UX & Accessibility: real `<text>` elements, per-panel accessible name (`aria-label`/`<title>`), contrast; wired into T016.

## Dependencies & Assumptions

- [X] CHK031 Are the stateless/persistence-excluded assumption and the "no new dependencies" claim validated/documented with rationale? [Assumption, Spec §Assumptions, Plan §Storage] — Plan §Storage, spec assumptions, constitution VI, and research §9 give rationale (stateless; no new tables/runtime deps).
- [X] CHK032 Is the "vector SVG scales at any zoom" assumption validated against rendering constraints? [Assumption, Spec §Assumptions] — Research §9 compares SVG vs backend-SVG-string vs canvas and validates SVG choice.
- [X] CHK033 Are cross-cutting dependencies (existing auth, regenerated OpenAPI client) explicitly referenced in requirements? [Dependency, Plan §Structure] — Auth referenced in research §8/contracts; regenerated client per principle V, plan §Structure, and T015.

## Ambiguities & Conflicts

- [X] CHK034 Are any terms ("consistent appearance", "distinct silhouette", "clean and geometric") specified with measurable visual criteria rather than subjective descriptors? [Ambiguity, Spec §Assumptions] — Identity as fixed constants makes appearance consistent (SC-002); silhouette is a concrete shape string (circle/square/triangle, research §7); geometric style is delivered by those fixed shapes.
- [X] CHK035 Is the demo cast of exactly three characters consistent with "two-character by construction" placement and the demo coverage of shout/speech/thought? [Conflict, Data §Panel, Spec §Assumptions] — Cast of 3 with two-character panels is consistent (research §6); demos cover speech/shout now and thought via T024 (quiet-tension), so the vocabulary is fully exercised.
