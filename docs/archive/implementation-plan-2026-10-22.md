# Historical record — superseded, not current instructions

## Historical plan and evidence (superseded for future scope)

The following is retained as historical evidence. Its approval, milestones and task instructions do not approve work under the new Criteria. Links and claims about current scope below reflect the old Criteria.

# Implementation Plan — Human-approved plan

Status: APPROVED BY HUMAN IN CHAT — 2026-10-22. M1 and M2 are Human-accepted; TASK-03 is complete. TASK-04 remains pending separate Human approval. Approved scope is unchanged.

Technical direction selected by the Human: rebuild the application structure in the existing Python/FastAPI and React/Vite stack, retain the local model runtime, and preserve the usability of existing Batch behavior and local project/output data.

GOALMAP is inside this Plan, not in CRITERIA. Each plan item starts with an observable GOAL tied to the approved CRITERIA sections. CRITERIA currently uses headings rather than numbered requirement IDs; links below point to those exact approved sections.

## GOALMAP

| Goal ID | Observable result | Approved CRITERIA reference | Dependencies | Plan section | State |
|---|---|---|---|---|---|
| G-01 | I can use the rebuilt app on this machine and continue using Batch and existing local project/output data. | [Scope](./CRITERIA.md#phạm-vi-sử-dụng-và-giới-hạn), [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn) | None | PLAN-01 | HUMAN ACCEPTED |
| G-02 | I can create and adjust concept frames with the approved editor tools and restore my work after reopening. | [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Success evidence](./CRITERIA.md#minh-chứng-thành-công) | G-01 | PLAN-02 | HUMAN ACCEPTED |
| G-03 | I can export correct assets, recover from per-frame failures, and complete ten edit/save/reopen/export cycles without losing saved work. | [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Success evidence](./CRITERIA.md#minh-chứng-thành-công) | G-01, G-02 | PLAN-03 | DRAFT |
| G-04 | Local regeneration and inpainting either demonstrably use the selected image/mask or remain clearly unavailable. | [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Open technical facts](./CRITERIA.md#open--chưa-xác-minh-về-mặt-kỹ-thuật) | G-01, G-02 | PLAN-04 | DRAFT |

## Plan items

### PLAN-01 — GOAL: I can run the rebuilt app locally and continue using Batch and my existing project/output data.

- **CRITERIA references:** [Scope](./CRITERIA.md#phạm-vi-sử-dụng-và-giới-hạn), [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn)
- **Current state / gap:** The M1 package entrypoint now binds the API to `127.0.0.1:8001`; settings can be redirected with `ASSETGEN_SETTINGS` for isolated runs. The file-based project/job/revision format and local model adapter remain unchanged. After correcting the smoke fixture to use the upload response, the backend suite passes 36 tests and the frontend build passes. A copied-data API smoke loaded all three existing projects, four jobs and six revision images without changing the original project tree. A live browser Batch run completed through the configured local model and saved a 512×512 WebP plus revision to an isolated output root. No separate pre-existing `outputs/` directory was present. The installed backend versions still differ from the pinned requirements.
- **Implementation:** Rebuild application structure in the selected stack without introducing remote services. Keep the model runtime local, bind services to loopback, and preserve existing project, job, revision and output data. Define the compatibility contract before changing storage; test migration/reading on copies, not user data. Retain current Batch behavior.
- **Dependencies:** None.
- **Acceptance:** The app is reachable only on the local machine; it can load a copy of existing project data, complete the documented Batch flow with the local model, and retain previous outputs/revisions. No cloud or remote endpoint is required.
- **Verification:** **Observed for TASK-02:** the backend suite passes 36 tests after the fixture correction; the frontend build passes; copied-data API checks loaded all three existing projects and served six revision images without changing the original project tree; the API listener was observed on loopback only; and a browser Batch run completed through the local model, saving a 512×512 WebP and revision to an isolated output root. The configured backend versions still differ from pinned requirements, and no separate pre-existing `outputs/` directory was available to copy. A separate-device reachability test and broader failure/retry checks remain unverified.
- **Limitations / risk / non-goals:** A full rewrite has higher compatibility and regression risk than targeted changes. There is no evidence that the existing stack is incapable; the Human selected a structural rebuild. Do not add multi-user, cloud, remote access or enterprise controls.

### PLAN-02 — GOAL: I can shape and manage concept frames with the approved editor tools, then reopen the project with my work intact.

- **CRITERIA references:** [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Success evidence](./CRITERIA.md#minh-chứng-thành-công)
- **Current state / gap:** The focused editor and local saved-state flow are implemented and passed browser E2E plus backend API tests; the Human accepted M2 after reviewing the evidence. The E2E uses isolated test storage and a synthetic selected-revision image; the export pipeline remains unverified and is reserved for PLAN-03.
- **Implementation:** Rebuild the concept workspace around source-image coordinates and the approved frame tools: rectangle/square/circle, selection, move, resize, duplicate, delete, undo/redo, zoom/pan, per-frame adjustable mask brush/eraser, crop preview and output settings. Save and restore project, frame, mask, revision selection and workflow step.
- **Dependencies:** G-01.
- **Acceptance:** A user can create rectangle, square, circle and a same-size duplicate at another position, adjust them, save, close/reopen and recover the correct source, geometry, masks, settings and step.
- **Verification:** **Observed for TASK-03:** 42 configured backend tests pass with isolated settings; the Playwright test passes in installed Chrome against loopback app/API servers. It exercised rectangle/square/circle creation, duplicate and geometry edits, undo/redo, delete, zoom, pan, adjustable brush/eraser and mask history, settings and crop preview, then closed and reopened the app page in the same browser context. It confirmed restored source crop, four frames, saved mask/settings, workflow step and a selected synthetic revision image. Backend tests cover invalid bounds/masks, step/revision state and revision-image retrieval. Frontend production build passes to an isolated output directory. This is local browser integration, not a browser-process or API restart test; the selected revision is fixture-seeded, not produced by export. Human reviewed and accepted M2; TASK-04 remains pending separate approval.
- **Limitations / risk / non-goals:** This is a focused concept editor, not a general photo editor with layers, filters, clone/retouch or color grading.

### PLAN-03 — GOAL: I can export each frame correctly and safely, including when one frame fails or I retry.

- **CRITERIA references:** [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Success evidence](./CRITERIA.md#minh-chứng-thành-công)
- **Current state / gap:** Crop/extraction and revision/output code exists, but the full editor-to-export journey and ten-cycle stability criterion have not been verified on the real host.
- **Implementation:** Rebuild queue, per-frame status/error reporting, preview, retry and revision history. Preserve earlier output/revisions on failures. Enforce requested dimensions, Fit/Fill, format, compression, size-limit reporting, circle alpha for PNG/WebP and background flattening for JPEG.
- **Dependencies:** G-01, G-02.
- **Acceptance:** One frame failure does not stop other frames; retry does not destroy previous output; output metadata and image pixels match the chosen settings. Ten consecutive edit/save/close/reopen/export cycles complete without crash or loss/change of saved data, with explicit errors and prior output preserved.
- **Verification:** Backend image/data tests plus live UI checks on representative PNG, WebP and JPEG cases; repeat the ten-cycle acceptance on the target Mac and retain observed evidence.
- **Limitations / risk / non-goals:** A maximum file-size target may be impossible for some images/settings; report the unmet target instead of claiming success.

### PLAN-04 — GOAL: I can use local concept regeneration/inpainting only when the output proves it used the selected image and mask.

- **CRITERIA references:** [Desired behavior](./CRITERIA.md#hành-vi-mong-muốn), [Open technical facts](./CRITERIA.md#open--chưa-xác-minh-về-mặt-kỹ-thuật)
- **Current state / gap:** Existing spike records these capabilities as pending visual verification. The adapter source contains local image/mask invocation paths, but the active runtime flags and resulting images have not been verified.
- **Implementation:** First run a bounded capability spike on the configured local runtime with before/after evidence for selected-image regeneration and masked inpainting. Only expose successful, verified actions; otherwise keep them unavailable and offer the approved unmasked crop/original-crop path.
- **Dependencies:** G-01, G-02.
- **Acceptance:** For each enabled operation, before/after images show the selected crop/revision was used and the selected mask was applied. If evidence is insufficient or the runtime cannot perform the operation, UI/API report it as unavailable and do not report success.
- **Verification:** Real local-model runs using the target runtime and saved inputs/masks; record runtime/model versions and inspect resulting images. Do not substitute mocked or text-to-image-only output.
- **Limitations / risk / non-goals:** Runtime capability and performance remain UNVERIFIED. No cloud API or speculative AI substitute is in scope.

## Review and delivery boundary

The Human approved this Plan and the milestone sequence in chat on 2026-10-22. M1 was subsequently accepted by the Human, and TASK-03 was separately approved and activated. These are recorded manual decisions, not an authenticated host gate. No Git integration target is set because this workspace is not a Git repository. Approved CRITERIA changes require the prescribed independent Advisor consultation. Do not claim authenticated gates or host enforcement.
