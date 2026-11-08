# AssetGen

Local batch image generation and a planned concept workflow. The Concept tab is currently an unconnected placeholder; HTML rendering and the ChatGPT/plugin bridge are not implemented. See [GSA handoff](docs/HANDOFF_GSA.md) for current priorities and boundaries.

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies with `corepack pnpm --dir frontend install --frozen-lockfile` (Node.js and Corepack required). The versions are pinned in `frontend/pnpm-lock.yaml`.

## Configuration

Copy `settings.example.json` to `settings.json` and edit it in the root directory. The real `settings.json` is intentionally not tracked. Ensure paths to models and binaries are correct for your machine.
For an isolated run, set `ASSETGEN_SETTINGS` to a separate settings JSON file; otherwise the root `settings.json` is used.

```json
{
  "model": {
    "diffusion_model": "/path/to/model.gguf",
    "llm_encoder": "/path/to/encoder.gguf",
    "vae": "/path/to/vae.safetensors",
    "vae_format": "flux2",
    "runtime_path": "/path/to/sd-cli"
  },
  "storage": {
    "output_root": "/path/to/outputs",
    "projects_root": "/path/to/projects"
  },
  "defaults": {
    "format": "webp",
    "compression": "balanced",
    "style_preset": "kideschool"
  }
}
```

### Tách nền (tuỳ chọn)

Đặt `remove_background: true` trong job để tách nền ảnh gốc bằng BiRefNet trước khi resize; kết quả có nền trong suốt (chỉ hỗ trợ `png` hoặc `webp`, `jpeg` sẽ báo lỗi). Ở chế độ `fit`, phần đệm cũng trong suốt, không dùng `background_color`. Mặc định tắt.

AssetGen không cài torch; việc tách nền chạy qua tiến trình con `backend/postprocess/bg_worker.py` bằng interpreter riêng. Cấu hình trong `settings.json`:

```json
"background_removal": {"enabled": false, "python": "/path/to/python-with-torch", "model": "ZhengPeng7/BiRefNet", "device": "mps"}
```

`python` phải trỏ tới interpreter đã cài torch, torchvision, transformers và Pillow. Giới hạn: lần chạy đầu có thể chậm (tải/nạp model, cần mạng nếu model chưa có trong cache HuggingFace); thiếu `python` hoặc worker lỗi/quá thời gian (mặc định 600 giây) thì job báo lỗi. Cờ `enabled` hiện chỉ là ghi chú cấu hình; tuỳ chọn được bật theo từng job qua `remove_background`.

## Running the Backend

Run the API server from the project root:
```bash
python3 -m backend.api
```
The API listens only on `http://127.0.0.1:8001`.

In another terminal, run `cd frontend && pnpm run dev` and open `http://127.0.0.1:5173`. On the configured Mac, `./start.command` starts both after dependencies are installed. Opening `frontend/index.html` directly with `file://` does not run the React app.

Run backend tests with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p '*.py' -v`. Test files use temporary directories. Build the frontend with `cd frontend && pnpm run build`.

The Batch screen includes a copyable [AI chat formatting template](frontend/prompt-template.txt). Send it to an AI chat and describe the assets you want. Paste its `=== ASSET ===` blocks directly into Batch or import them as a UTF-8 `.txt` file.

Each block may also set optional keys before `prompt:`: `width` and `height` (together), `max_kb`, `format` (`png|webp|jpeg`), `compression` (`lossless|balanced|smallest`), `fit` (`fit|fill`) and `remove_background` (`true|false`). Keys set in a block override the Batch screen defaults for that asset; invalid values, duplicate keys and `format: jpeg` with `remove_background: true` are reported as parse errors.

### Chạy một lệnh (dành cho AI)

```bash
python3 scripts/assetgen_run.py BLOCKS.txt --out ./ra [--project TÊN] [--timeout 600]
```

Script tự bật server nếu chưa chạy (và tắt khi xong), tải block lên, tạo project và job, sinh ảnh, chờ xong rồi sao chép ảnh vào `--out`. Stdout là JSON tóm tắt (từng job: `status`, `error`, tệp, KB, kích thước ảnh, `has_alpha`); tiến độ ở stderr; mã thoát 0 chỉ khi mọi job COMPLETED (block lỗi parse thì in lỗi, thoát khác 0, không tạo job). Ví dụ block:

```
=== ASSET ===
name: tiger-icon
ratio: 1:1
width: 256
height: 256
max_kb: 15
format: webp
remove_background: true
prompt: glossy soft 3D toy style, clean white background, no text, a cheerful tiger cub mascot waving
=== END ===
```

Lưu ý: các khoá tuỳ chọn (`width`, `height`, `max_kb`, `format`, `compression`, `fit`, `remove_background`) phải đặt TRƯỚC `prompt:`, vì mọi dòng sau `prompt:` là nội dung prompt.

Click Generate after importing prompts. The app creates a project automatically if needed and opens Gallery to show each job's status and output. The local FLUX.2 Klein adapter uses four steps and CFG 1.0 from `settings.json`.

Completed images are collected automatically in `outputs/<project-id>/`. This folder contains images only. Each file uses the prompt's `name` (for example, `name: Math Card 01` produces `Math Card 01.webp`). Gallery has buttons to open the folder or copy its path. Click any image in Gallery to edit its prompt and regenerate it. Once the new image finishes, it replaces the file of the same name in this folder; earlier revisions remain in internal project storage.

## Concept workflow status

The Concept tab is a temporary placeholder, not a working renderer. The former frame/crop/mask interface has been removed; legacy concept-only backend routes and processing were removed; existing project and image data remain. The future workflow and its unverified ChatGPT Web/plugin/tunnel boundary are described in [Criteria](docs/CRITERIA.md), [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) and [Technical Proposal](docs/TECHNICAL_PROPOSAL.md).

For the current placeholder browser test, run a local Vite server and then:

```bash
ASSETGEN_FRONTEND_URL=http://127.0.0.1:5173 PLAYWRIGHT_CHANNEL=chrome \
  corepack pnpm --dir frontend exec playwright test concept-placeholder.spec.ts
```

## API Endpoints

- `POST /projects`: Create a project.
- `POST /batch/upload`: Preview and validate a prompt file.
- `POST /projects/{project_id}/batch/jobs`: Validate and save edited jobs.
- `POST /batch/generate`: Queue saved jobs.
- `GET /batch/status`: Read progress and selected revision image URLs.
- `POST /batch/regenerate`: Edit one image prompt and queue a new revision.
- `POST /project/export`: Export selected revisions.

Legacy concept editor backend endpoints have been removed. Existing legacy concept job files remain on disk but are not shown as Batch jobs. HTML rendering and plugin integration are not implemented.
