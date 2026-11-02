from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Body, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
import re
import uuid
import logging
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from ..config import load_settings
from ..projects.manager import ProjectManager
from ..generation.parser import PromptParser
from ..postprocess.engine import OutputEngine
from ..queue.engine import GenerationQueue
from ..generation.adapter import ModelAdapter
from ..projects.models import TextAssetJob, Revision

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

settings = load_settings()

pm = ProjectManager(settings["storage"]["projects_root"])
queue = GenerationQueue()
parser = PromptParser()
engine = OutputEngine(settings["storage"]["output_root"])
adapter = ModelAdapter(settings)
queue = GenerationQueue()

def recover_interrupted_jobs():
    root = Path(settings["storage"]["projects_root"])
    if not root.exists():
        return
    for project_file in root.glob("*/project.json"):
        project_id = project_file.parent.name
        for job in pm.load_jobs(project_id):
            if job.status in {"QUEUED", "GENERATING", "POSTPROCESSING"}:
                job.status = "INTERRUPTED"
                job.error = "Application stopped before the job finished"
                pm.save_job(project_id, job)

def project_root_for(project_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", project_id):
        raise HTTPException(status_code=400, detail={"code": "INVALID_PROJECT_ID", "message": "Invalid project ID", "details": {}})
    root = Path(settings["storage"]["projects_root"]) / project_id
    if not (root / "project.json").is_file():
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found", "details": {}})
    return root

def image_folder_for(project_id: str) -> Path:
    project_root_for(project_id)
    return Path(settings["storage"]["output_root"]) / project_id

def image_filename(job: TextAssetJob, suffix: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", job.name).strip(" .")
    if not name or name in {".", ".."}:
        name = job.id
    return f"{name}{suffix}"

def publish_image(project_id: str, job: TextAssetJob, source: Path) -> str:
    folder = image_folder_for(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = image_filename(job, source.suffix)
    destination = folder / filename
    temporary = folder / f".{job.id}.{uuid.uuid4().hex}.tmp"
    try:
        shutil.copyfile(source, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return filename

@app.post("/projects")
async def create_project(name: str = Form(...)):
    return pm.create_project(name.strip(), settings["storage"]["output_root"]).model_dump(mode="json")

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    project_root_for(project_id)
    return pm.load_project(project_id).model_dump(mode="json")

@app.post("/projects/{project_id}/batch/jobs")
async def save_batch_jobs(project_id: str, jobs: List[dict] = Body(...)):
    project_root_for(project_id)
    errors = []
    parsed = []
    slugs = set()
    existing_by_slug = {parser.normalize_name(job.name): job.id for job in pm.load_jobs(project_id)}
    for index, raw in enumerate(jobs):
        name = str(raw.get("name", "")).strip()
        prompt = str(raw.get("prompt", "")).strip()
        ratio = raw.get("ratio")
        slug = parser.normalize_name(name)
        if not name or not slug or slug in slugs:
            errors.append({"asset": index, "field": "name", "code": "INVALID_OR_DUPLICATE_NAME"})
        if not prompt:
            errors.append({"asset": index, "field": "prompt", "code": "MISSING_PROMPT"})
        if ratio and not re.fullmatch(r"[1-9]\d*:[1-9]\d*", str(ratio)):
            errors.append({"asset": index, "field": "ratio", "code": "INVALID_RATIO"})
        slugs.add(slug)
        try:
            parsed_job = TextAssetJob.model_validate(raw)
            uuid.UUID(parsed_job.id)
            if pm.is_legacy_job_id(project_id, parsed_job.id):
                errors.append({"asset": index, "field": "id", "code": "LEGACY_JOB_ID_CONFLICT"})
            if slug in existing_by_slug and existing_by_slug[slug] != parsed_job.id:
                errors.append({"asset": index, "field": "name", "code": "DUPLICATE_PROJECT_SLUG"})
            parsed.append(parsed_job)
        except Exception as exc:
            errors.append({"asset": index, "field": None, "code": "INVALID_JOB", "message": str(exc)})
    if errors:
        raise HTTPException(status_code=422, detail={"code": "BATCH_VALIDATION_FAILED", "message": "Fix batch errors before saving", "details": errors})
    for job in parsed:
        pm.save_job(project_id, job)
    return {"count": len(parsed), "job_ids": [job.id for job in parsed]}

@app.get("/projects/{project_id}/revisions/{job_id}/{revision_id}/image")
async def get_revision_image(project_id: str, job_id: str, revision_id: str):
    project_root = project_root_for(project_id)
    if not all(re.fullmatch(r"[0-9a-fA-F-]{36}", value) for value in (job_id, revision_id)):
        raise HTTPException(status_code=400, detail="Invalid revision ID")
    revision_file = project_root / "revisions" / job_id / f"{revision_id}.json"
    if not revision_file.is_file():
        raise HTTPException(status_code=404, detail="Revision not found")
    revision = Revision.model_validate_json(revision_file.read_text(encoding="utf-8"))
    image_path = (project_root / revision.image_path).resolve()
    if not image_path.is_relative_to(project_root.resolve()) or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Revision image not found")
    return FileResponse(image_path)

@app.on_event("startup")
async def startup_event():
    # Start queue in background
    recover_interrupted_jobs()
    app.state.queue_task = asyncio.create_task(queue.run())

@app.on_event("shutdown")
async def shutdown_event():
    queue.shutdown()
    await app.state.queue_task

@app.post("/project/export")
async def export_project(project_id: str = Form(...)):
    project_root_for(project_id)
    try:
        project = pm.load_project(project_id)
        jobs = pm.load_jobs(project_id)
        if not any(job.selected_revision_id for job in jobs):
            raise ValueError("No selected revisions to export")

        export_root = Path(settings["storage"]["output_root"]) / "exports"
        export_root.mkdir(parents=True, exist_ok=True)
        export_id = uuid.uuid4().hex
        export_dir = export_root / f"export_{project_id}_{export_id}"
        staging_dir = export_root / f".export_{project_id}_{export_id}.tmp"
        staging_dir.mkdir()

        manifest = {
            "project_id": project_id,
            "project_name": project.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "assets": []
        }

        # Copy selected revisions to export folder
        for job in jobs:
            if job.selected_revision_id:
                project_root = Path(settings["storage"]["projects_root"]) / project_id
                revision_file = project_root / "revisions" / job.id / f"{job.selected_revision_id}.json"
                if not revision_file.exists():
                    raise FileNotFoundError(f"Selected revision {job.selected_revision_id} not found")
                revision = Revision.model_validate_json(revision_file.read_text(encoding="utf-8"))
                rev_path = (project_root / revision.image_path).resolve()
                if not rev_path.is_relative_to(project_root.resolve()) or not rev_path.is_file():
                    raise FileNotFoundError(f"Revision image invalid: {revision.image_path}")
                dest_path = staging_dir / f"{job.id}_{job.selected_revision_id}{rev_path.suffix}"
                shutil.copyfile(rev_path, dest_path)
                manifest["assets"].append({"job_id": job.id, "name": job.name, "file": dest_path.name})

        with open(staging_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        staging_dir.rename(export_dir)

        return {"status": "success", "export_path": str(export_dir)}
    except Exception as e:
        if "staging_dir" in locals() and staging_dir.exists():
            shutil.rmtree(staging_dir)
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/batch/upload")
async def upload_batch(file: UploadFile):
    try:
        content = (await file.read()).decode("utf-8")
    except Exception as e:
        print(f"UPLOAD ERROR: {e}")
        raise HTTPException(status_code=422, detail={"code": "INVALID_UTF8", "message": str(e), "details": {}})
    jobs, errors = parser.parse(content)

    # Apply default target sizes from settings (simulated)
    for job in jobs:
        job.target_width = 512
        job.target_height = 512

    return {
        "jobs": [job.dict() for job in jobs],
        "errors": errors,
        "count": len(jobs)
    }

async def process_job(job_id: str, project_id: str):
    try:
        # 1. Load job
        jobs = pm.load_jobs(project_id)
        job = next((j for j in jobs if j.id == job_id), None)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # 2. Generate
        # Update status in project (simulated since pm.save_job is needed)
        job.status = "GENERATING"
        attempt_id = uuid.uuid4().hex
        job.attempts.append({"id": attempt_id, "started_at": datetime.now(timezone.utc).isoformat(), "status": "GENERATING"})
        pm.save_job(project_id, job)

        # Resolve seed
        import random
        if job.seed == -1:
            job.seed = random.randint(0, 2**32 - 1)
            pm.save_job(project_id, job)

        # Actual inference
        # Create a temporary output path for the adapter
        temp_output = os.path.join(settings["storage"]["output_root"], f"tmp_{job.id}.png")
        Path(settings["storage"]["output_root"]).mkdir(parents=True, exist_ok=True)
        result = await asyncio.to_thread(adapter.generate_text_asset, job, temp_output)

        # 3. Postprocess
        job.status = "POSTPROCESSING"
        pm.save_job(project_id, job)

        from PIL import Image
        with Image.open(temp_output) as img:
            from ..projects.models import OutputSettings
            out_settings = OutputSettings(
                width=job.target_width,
                height=job.target_height,
                format=job.output_format,
                compression=job.compression_mode,
                fit_mode=job.fit_mode,
                max_kb=job.max_kb,
                background_color=job.background_color
            )
            final_path, metadata = engine.process(img, out_settings)

        # 4. Save Revision
        revision = Revision(
            source_job_id=job.id,
            image_path=final_path,
            seed=job.seed,
            width=metadata["dimensions"][0],
            height=metadata["dimensions"][1],
            file_size=metadata["final_size"],
            warnings=metadata.get("warnings", [])
        )
        project_root = Path(settings["storage"]["projects_root"]) / project_id
        revision_dir = project_root / "revisions" / job.id
        revision_dir.mkdir(parents=True, exist_ok=True)
        final_in_project = revision_dir / f"{revision.revision_id}{Path(final_path).suffix}"
        shutil.move(final_path, final_in_project)
        revision.image_path = str(final_in_project.relative_to(project_root))
        pm.save_revision(project_id, revision)
        job.output_filename = publish_image(project_id, job, final_in_project)

        # 5. Complete
        job.status = "COMPLETED"
        job.error = None
        job.selected_revision_id = revision.revision_id
        job.attempts[-1].update({"status": "COMPLETED", "revision_id": revision.revision_id, "finished_at": datetime.now(timezone.utc).isoformat()})
        pm.save_job(project_id, job)

        # Cleanup temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)

    except Exception as e:
        # Handle failure
        jobs = pm.load_jobs(project_id)
        job = next((j for j in jobs if j.id == job_id), None)
        if job:
            job.status = "FAILED"
            job.error = str(e)
            if job.attempts:
                job.attempts[-1].update({"status": "FAILED", "error": str(e), "finished_at": datetime.now(timezone.utc).isoformat()})
            pm.save_job(project_id, job)
        raise

@app.post("/batch/generate")
async def generate_batch(project_id: str = Form(...)):
    project_root_for(project_id)
    jobs = pm.load_jobs(project_id)
    ready_jobs = [j for j in jobs if j.status == "READY"]

    for job in ready_jobs:
        if queue.enqueue(job.id, lambda j_id=job.id: process_job(j_id, project_id)):
            job.status = "QUEUED"
            pm.save_job(project_id, job)

    return {"status": "queued", "project_id": project_id, "count": len(ready_jobs)}

@app.post("/batch/regenerate")
async def regenerate_image(project_id: str = Form(...), job_id: str = Form(...), prompt: str = Form(...)):
    project_root_for(project_id)
    job = next((item for item in pm.load_jobs(project_id) if item.id == job_id), None)
    if not isinstance(job, TextAssetJob):
        raise HTTPException(status_code=404, detail="Image not found")
    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")
    if job.status in {"QUEUED", "GENERATING", "POSTPROCESSING"}:
        raise HTTPException(status_code=409, detail="Image is already generating")
    if not queue.enqueue(job.id, lambda: process_job(job.id, project_id)):
        raise HTTPException(status_code=409, detail="Image is already in the queue")
    job.prompt = prompt
    job.seed = -1
    job.error = None
    job.status = "QUEUED"
    pm.save_job(project_id, job)
    return {"status": "queued", "job_id": job.id}

@app.post("/projects/{project_id}/open-image-folder")
async def open_image_folder(project_id: str):
    folder = image_folder_for(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    if os.name != "posix":
        raise HTTPException(status_code=501, detail="Opening folders is supported on macOS")
    try:
        subprocess.Popen(["open", str(folder)])
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"folder": str(folder)}

@app.post("/batch/retry")
async def retry_jobs(project_id: str = Form(...), job_ids: Optional[str] = Form(None)):
    project_root_for(project_id)
    jobs = pm.load_jobs(project_id)

    if job_ids:
        target_ids = job_ids.split(",")
        jobs_to_retry = [j for j in jobs if j.id in target_ids and j.status in ("FAILED", "INTERRUPTED")]
    else:
        jobs_to_retry = [j for j in jobs if j.status in ("FAILED", "INTERRUPTED")]

    for job in jobs_to_retry:
        job.status = "READY"
        pm.save_job(project_id, job)
        if queue.enqueue(job.id, lambda j_id=job.id: process_job(j_id, project_id)):
            job.status = "QUEUED"
            pm.save_job(project_id, job)

    return {"status": "retrying", "count": len(jobs_to_retry)}

@app.post("/batch/cancel")
async def cancel_jobs(project_id: str = Form(...), job_id: Optional[str] = Form(None)):
    project_root_for(project_id)
    if job_id:
        # Cancel specific job
        success = queue.cancel_job(job_id)
        # Also update in project storage
        jobs = pm.load_jobs(project_id)
        job = next((j for j in jobs if j.id == job_id), None)
        if job and success:
            job.status = "SKIPPED"
            pm.save_job(project_id, job)
        return {"status": "cancelled" if success else "not_in_queue", "job_id": job_id}
    else:
        # Cancel all pending
        queue.cancel_all_pending()
        jobs = pm.load_jobs(project_id)
        for job in jobs:
            if job.status == "QUEUED":
                job.status = "SKIPPED"
                pm.save_job(project_id, job)
        return {"status": "all_cancelled"}

@app.get("/batch/status")
async def get_batch_status(project_id: str):
    project_root_for(project_id)
    jobs = pm.load_jobs(project_id)
    return {
        "project_id": project_id,
        "image_folder": str(image_folder_for(project_id)),
        "jobs": [
            {
                "id": j.id,
                "name": j.name,
                "status": j.status,
                "error": j.error,
                "prompt": j.prompt if isinstance(j, TextAssetJob) else None,
                "output_filename": j.output_filename,
                "selected_revision": j.selected_revision_id,
                "image_url": f"/projects/{project_id}/revisions/{j.id}/{j.selected_revision_id}/image" if j.selected_revision_id else None
            }
            for j in jobs
        ]
    }

if __name__ == "__main__":
    from .runtime import run
    run(app)
