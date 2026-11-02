import json
import os
import shutil
from pathlib import Path
from typing import List
from .models import Project, TextAssetJob, Revision

class ProjectManager:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def create_project(self, name: str, output_root: str) -> Project:
        project = Project(name=name, output_root=output_root)
        self.save_project(project)
        return project

    def save_project(self, project: Project):
        project_dir = self.root_dir / project.id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Atomic write for project.json
        temp_file = project_dir / "project.json.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(project.model_dump_json(indent=2))
        temp_file.replace(project_dir / "project.json")

    def load_project(self, project_id: str) -> Project:
        project_file = self.root_dir / project_id / "project.json"
        if not project_file.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        with open(project_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Simple migration hook
            version = data.get("schema_version", 1)
            if version < 1:
                # Handle migration to v1
                data["schema_version"] = 1

            return Project.model_validate(data)

    def is_legacy_job_id(self, project_id: str, job_id: str) -> bool:
        path = self.root_dir / project_id / "jobs" / f"{job_id}.json"
        if not path.is_file():
            return False
        data = json.loads(path.read_text(encoding="utf-8"))
        return "source_image" in data and "ratio" not in data

    def save_job(self, project_id: str, job: TextAssetJob):
        if self.is_legacy_job_id(project_id, job.id):
            raise ValueError("Cannot overwrite a legacy concept job")
        jobs_dir = self.root_dir / project_id / "jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)

        job_file = jobs_dir / f"{job.id}.json"
        temp_file = job_file.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(job.model_dump_json(indent=2))
        temp_file.replace(job_file)

    def load_jobs(self, project_id: str) -> List[TextAssetJob]:
        jobs_dir = self.root_dir / project_id / "jobs"
        if not jobs_dir.exists():
            return []

        jobs = []
        for file in jobs_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Keep legacy concept records on disk, without loading or rewriting them.
                if "source_image" in data and "ratio" not in data:
                    continue
                jobs.append(TextAssetJob.model_validate(data))
        return jobs

    def save_revision(self, project_id: str, revision: Revision):
        rev_dir = self.root_dir / project_id / "revisions" / revision.source_job_id
        rev_dir.mkdir(parents=True, exist_ok=True)

        rev_file = rev_dir / f"{revision.revision_id}.json"
        temp_file = rev_file.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(revision.model_dump_json(indent=2))
        temp_file.replace(rev_file)
