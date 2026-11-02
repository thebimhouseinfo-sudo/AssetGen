# Historical record — superseded, not current instructions

## Historical milestones (superseded for future scope)

Retained as historical evidence; old approval does not authorize work under the revised Criteria.

# Milestones — Human-approved sequence

Status: APPROVED BY HUMAN IN CHAT — 2026-10-22. M1 and M2 are Human-accepted. TASK-04 and TASK-05 remain pending separate Human approval.

Milestones are derived from the current Plan and approved CRITERIA. Completion is evidence-based and reviewed manually; there is no automatic approval or push.

## M1 — Local foundation and data compatibility

- **Plan goals:** G-01
- **Exit evidence:** Rebuilt app starts on loopback only; existing project/output copies remain readable; documented Batch flow works with the configured local model; backend verification suite passes after the known fixture/API contract mismatch is resolved; frontend build passes.
- **Observed:** API listener at `127.0.0.1:8001`; copied existing project data loaded and revision images served without changing the original tree; a live Batch generation completed through the local model to isolated output; backend suite passed 36 tests; frontend build passed to temporary output. No separate pre-existing `outputs/` directory was present.
- **Review trigger:** Completed — Human reviewed the M1 evidence and confirmed acceptance before approving TASK-03.
- **Risks / boundaries:** Preserve user data; no remote service, cloud model or enterprise control. Actual target model/runtime compatibility must be evidenced.

## M2 — Concept editor and saved state

- **Plan goals:** G-02
- **Exit evidence:** Live UI demonstrates rectangle, square, circle and duplicate frame creation/editing; undo/redo, zoom/pan and adjustable mask brush/eraser work; saved project restores source, frames, masks, settings, selected revision and step.
- **Observed:** Independent Tester confirmed the Playwright browser E2E passed against isolated loopback services. It exercised the editor tools, mask/settings persistence, app-page close/reopen in the same browser context, step restoration and a seeded selected-revision image. The 42-test backend suite and isolated frontend production build also passed. The revision image is a synthetic fixture, not a verified export.
- **Review trigger:** Human reviews the editor workflow and recovery after reopening.
- **Review status:** Completed — Human accepted M2 in this chat after reviewing the recorded evidence. This does not approve export or local AI capability work.
- **Risks / boundaries:** This is not a general-purpose photo editor. AI regeneration/inpainting stays unavailable until M4 evidence.

## M3 — Reliable export and repeated use

- **Plan goals:** G-03
- **Exit evidence:** Four-frame acceptance project produces correct count, names, dimensions, formats and alpha; per-frame failures and retry preserve prior results; ten consecutive edit/save/close/reopen/export cycles complete without crash or saved-data loss/change.
- **Review trigger:** Human reviews output correctness and ten-cycle evidence on the target Mac.
- **Risks / boundaries:** Report a missed size target clearly; do not silently reduce dimensions or overwrite prior revisions.

## M4 — Local AI capability evidence and availability

- **Plan goals:** G-04
- **Exit evidence:** Real local-model before/after evidence proves image-conditioned regeneration and mask-conditioned inpainting. If either capability is not verified, that action remains unavailable and does not produce a success-shaped response.
- **Review trigger:** Human reviews the resulting images and decides whether the capability is acceptable to expose.
- **Risks / boundaries:** No cloud APIs or mocked substitute; runtime, model support and performance remain open until measured.

## Task and integration policy

The Plan and milestone sequence are Human-approved. M1 and M2 are Human-accepted; TASK-03 is complete. TASK-04 and TASK-05 still await separate Human approval before becoming Active. Each approved task must map to exactly one current GOAL and measurable exit evidence. Keep assignment, reviews and any publication manual. No branch or push target is declared because this workspace is not a Git repository.
