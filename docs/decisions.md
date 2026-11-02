# Technical Decisions — AssetGen

## Hardware and Environment
- **Machine:** Apple Silicon Mac
- **OS:** macOS (Darwin 25.6.0)
- **Python:** 3.10
- **Runtime:** `stable-diffusion.cpp` (Metal enabled)

## Model Weights
- **Diffusion Model:** FLUX.2 Klein 4B GGUF (Q6_K)
  - Source: Unsloth / HuggingFace
  - File: `Rawmodel/flux-2-klein-4b-Q6_K.gguf`
- **Text Encoder:** Qwen3-4B GGUF (Q4_K_M)
  - File: `Rawmodel/qwen3-4b-q4_k_m.gguf`
- **VAE:** FLUX.2 VAE
  - File: `Rawmodel/flux2_ae.safetensors`

## Performance Metrics (Spike)
The earlier estimates here conflicted with `spike_results.md` and have no attached measurement log. Re-run and record cold/warm timings, resolution, peak unified memory, and ten consecutive requests before accepting performance figures.

## Capability Verification
- **Text-to-Image:** PASS
- **Concept Regeneration:** PENDING (Awaiting visual evidence)
- **Delete & Fill:** PENDING (Awaiting visual evidence)
