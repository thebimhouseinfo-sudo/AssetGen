> Historical host snapshot (2026-10-22): concept-editor and offline-only direction below is superseded. For current approved direction and verified status, read [Implementation Plan](./IMPLEMENTATION_PLAN.md), [Technical Proposal](./TECHNICAL_PROPOSAL.md), and [handoff](./HANDOFF_GSA.md). Host paths and versions require fresh verification.

# Architecture — current state and approved direction

Status: Human-selected direction is approved. TASK-02 establishes the local runtime/configuration foundation; later milestones rebuild and verify the concept editor and export workflows.

## Current implementation
- The frontend is a React/Vite browser application. Its development server is configured for `127.0.0.1:5173`.
- The backend is a FastAPI application. Batch requests are parsed and saved as JSON jobs; an in-process queue invokes the configured local model executable through `ModelAdapter`; postprocessing and revision metadata are handled by backend modules.
- Project, job and revision metadata are file-based under the configured project root. Project JSON has a `schema_version`; writes use temporary files followed by rename. Generated output images are stored under the configured output root.
- The Concept workspace now supports source-image-coordinate rectangles, squares and circles; selection, movement, resizing, duplicate/delete, undo/redo, zoom and pan; per-frame adjustable mask editing; previews and output settings. Project, frame, mask, setting, selected-revision and workflow-step state use the existing local project storage.
- The editor and saved-state flow have browser E2E coverage. Masks are preserved but are not applied to source crops. The unverified regeneration endpoint returns HTTP 501 (`CONCEPT_REGENERATION_UNVERIFIED`); concept export correctness and repeated-use reliability remain pending TASK-04.
- The backend now starts through `backend.api` and listens on `127.0.0.1:8001`; the frontend development server is loopback-bound at `127.0.0.1:5173`.
- `backend.config.load_settings` loads the root `settings.json` by default. `ASSETGEN_SETTINGS` selects a separate settings file for isolated runs and copy-based tests.
- The Batch API, file-based project manager, queue and local model adapter remain in their existing modules for M1 compatibility. No project/job/revision schema migration was introduced.

## Human-selected technical direction
- Rebuild the application structure using the existing Python/FastAPI and React/Vite stack.
- Retain the configured local model runtime and make existing Batch behavior, projects, outputs and revisions usable after the rewrite.
- Keep the application for one user on one machine; do not introduce cloud AI, remote access, collaboration or enterprise administration.

## Target constraints and unresolved design
- Bind all application services to loopback only. The API listener was observed at `127.0.0.1:8001`; the frontend listener is configured at `127.0.0.1:5173`.
- Preserve existing local data and stable frame/job/revision identities. The M1 smoke test loaded copies of the three existing projects and their revision images without modifying the originals. No schema transition was needed.
- Rebuild the concept editor around the approved frame, mask, preview, persistence and export behaviors. AI regeneration and inpainting remain unavailable until a real local-model before/after test verifies the selected image and mask are used.
- Keep the single-user architecture proportionate. No database server, remote service or enterprise security layer is approved by the product criteria.
- Broader module boundaries for the concept editor/export rebuild, supported dependency versions, local runtime version/flags and additional verification commands remain open.

## M1 evidence boundary
- The live browser Batch flow completed one prompt through the configured local model and saved a 512×512 WebP plus revision under an isolated output root.
- The configured output root did not exist before the test, so no prior standalone output files were available to copy. Existing project-stored revision images were copied and served successfully.
- This establishes one local generation path, not repeated-use reliability, concept editing, or regeneration/inpainting capability.

This document describes how the application currently works and the Human-selected technical direction. Product behavior remains defined only by `docs/CRITERIA.md`.
