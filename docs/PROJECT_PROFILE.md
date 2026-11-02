> Historical host snapshot (2026-10-22): concept-editor and offline-only direction below is superseded. For current approved direction and verified status, read [Implementation Plan](./IMPLEMENTATION_PLAN.md), [Technical Proposal](./TECHNICAL_PROPOSAL.md), and [handoff](./HANDOFF_GSA.md). Host paths and versions require fresh verification.

# Technical profile — evidence snapshot, 2026-10-22

Status: PARTIALLY VERIFIED. Facts below describe the current workspace; they do not certify the model runtime or real-host behavior.

## Project and host
- Existing local image-generation application with a browser UI and a Python API.
- Current development host: macOS Darwin 25.6.0, arm64.
- Installed tools: Python 3.9.6, Node.js 24.21.0, npm 11.19.0. `pnpm` is not available on PATH; Corepack supplies pnpm 12.14.0 for the frontend's lockfile-v9 project.
- The hardware model and memory available to the application are not verified. `docs/decisions.md` and `spike_results.md` contain historical hardware/runtime claims, not a current host measurement.

## Stack and dependency evidence
- Backend source uses Python, FastAPI and Pydantic. `requirements.txt` pins FastAPI 0.115.0, Uvicorn 0.30.6, Pydantic 2.8.2, python-multipart 0.0.12 and Pillow 10.4.0.
- The active Python environment has FastAPI 0.128.8, Uvicorn 0.39.0, Pydantic 2.13.5 and Pillow 11.3.0. These differ from the pinned requirements. The installed python-multipart version was not checked.
- Frontend uses React 18.3.1, React DOM 18.3.1 and Vite 5.4.8, with a `pnpm-lock.yaml`.
- The frontend E2E runner is `@playwright/test` 1.64.1. Installed Chrome was used for local browser integration tests. `frontend/pnpm-workspace.yaml` explicitly allows only the existing `esbuild` install script, after Human approval.
- Human-selected technical direction: rebuild the application structure using the existing Python/FastAPI and React/Vite stack, retain the local model runtime, and keep existing Batch behavior and local project/output data usable.

## Runtime and interfaces
- The model adapter invokes a configured local runtime executable with model, encoder and VAE paths. The configured paths, runtime version and a fresh inference run have not been verified in this session.
- Historical `spike_results.md` records text-to-image as passed; concept regeneration and delete/fill are still pending visual verification. A fresh local Batch inference also completed in the isolated smoke test below.
- The frontend development script binds to `127.0.0.1:5173`. The backend package entrypoint binds to `127.0.0.1:8001`; an actual listener check confirmed the API was not bound to a wildcard interface. CORS allows the two localhost frontend origins.
- `backend.config.load_settings` uses the root `settings.json` by default. `ASSETGEN_SETTINGS` can point to a separate settings JSON for isolated runs without changing the user's configured data roots.
- No external AI service or remote deployment has been verified or is in scope.

## Build and test evidence
- Backend suite passes: 42 tests via `ASSETGEN_SETTINGS=<isolated-settings.json> python3 harness/common/verify.py`. The original `test_batch_workflow` fixture was invalid/incomplete; it now uses the job payload returned by the preceding upload step. No behavior assertion was weakened.
- `main.py` still emits a Pydantic deprecation warning for `.dict()`; it does not fail the suite.
- Frontend production build passes to an isolated directory with `corepack pnpm --dir frontend exec vite build --outDir <temporary-directory>`.
- The Playwright E2E test passes in installed Chrome against loopback frontend/API servers using isolated settings. It covers frame tools and geometry, mask editing and recovery, saved output settings, closing/reopening the app page, workflow-step restoration, and loading a seeded selected-revision image. The revision image is a synthetic test fixture, not an export result.
- `harness/common/checks.json` configures the verified backend suite; the shared runner reports that check PASS. Frontend build and browser integration remain separate manual checks. E2E uses a test-created revision fixture inside the isolated project root.
- A live API process using `python3 -m backend.api` served on `127.0.0.1:8001`. With a copied projects directory and isolated output root, the API loaded all 3 existing projects, 4 jobs and served 4 existing revision images. The original project tree hash was unchanged. No pre-existing `outputs/` directory existed to copy.
- In the live browser UI, a one-asset Batch prompt completed through the configured local model. The isolated test copy contained one generated 512×512 WebP and its revision; no user project/output roots were used.
- Browser close/reopen was tested by closing and reopening app pages in one browser context; a full browser-process/backend restart was not tested. No concept export acceptance or ten-cycle repeated-use test has been completed. Offline/network-isolation from another device and post-lock tests remain unverified.

## Agent workflow configuration
- `.agents/config/worker-context.yaml` points Coder and Tester to generic skills; both knowledge lists are empty. No project-specific skill or knowledge pack is configured.
- The config identifies Google Antigravity IDE as its intended host. Native role/skill/hook execution and enforcement have not been verified in a live host.

## Open facts
- Supported Python/Node versions and dependency installation procedure must be settled against the intended host; current installed backend versions differ from the manifest even though the current backend suite passes.
- Exact local model/runtime version compatibility, regeneration/inpainting capability, broader model performance and target machine resource limits remain UNVERIFIED.
- The Plan and milestone sequence for the full rewrite are Human-approved. Detailed module boundaries and full live-host/browser/model verification remain open.

Bootstrap records observed evidence only. Do not infer that installed files prove a working model, or that prompt-level instructions/hook configuration prove native host enforcement.
