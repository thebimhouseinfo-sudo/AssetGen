# AssetGen Technical Spike Results

## Task 0.0 — Minimal UI Gate
- **Status:** PASSED
- **Verification:**
    - `sd-cli` generates PNG: Yes
    - UI generates PNG: Yes
    - Prompt change affects image: Yes
    - Reproducibility: Seed locking works (verified via `sd-cli`)
    - 10 consecutive runs: Stable, no crashes.

## Task 0.1 — Model Runtime Check
- **Hardware:** MacBook Pro M1 Max, 64GB RAM
- **Runtime:** stable-diffusion.cpp (bin version master-748-68f3d6d)
- **Model:** flux-2-klein-4b-Q6_K.gguf
- **Text Encoder:** qwen3-4b-q4_k_m.gguf
- **VAE:** flux2_ae.safetensors

### Measurements
- **Cold Start Time:** ~10-12s (model loading)
- **Inference Time (512x512):** ~15-20s per iteration (total ~200-300s for 20 steps)
- **Peak Memory:** ~7GB VRAM (total params memory size)
- **Stability:** Stable on M1 Max

## Task 0.2 — Text-to-image spike
- **Status:** PASSED
- **Findings:** Successfully generated images with multiple ratios (1:1, 4:3, etc.). Seed locking is functional.

## Task 0.3 — Concept regeneration spike
- **Status:** PENDING visual verification
- **Evidence:** `spike_outputs/concept_sample.jpg`
- **Prior observation (unverified):** The output may be a regenerated asset rather than a crop. Source/region and before/after pairs are still needed to verify this claim.

## Task 0.4 — Delete & Fill spike
- **Status:** PENDING visual verification
- **Evidence:** `spike_outputs/concept_test.png`, `spike_outputs/mask.png`
- **Prior observation (unverified):** Reconstruction was reported, but the saved evidence is insufficient for the visual acceptance gate.
- **Test Cases:**
    - Text over artwork: before/after pair and reviewer notes needed.
    - Button over image: before/after pair and reviewer notes needed.
    - No transparent holes: inspect the saved image and record the result.
