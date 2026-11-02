from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union, Literal
from datetime import datetime, timezone
import uuid

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    output_root: str
    style_preset: Optional[str] = None
    schema_version: int = 1

class OutputSettings(BaseModel):
    width: int = Field(default=512, gt=0)
    height: int = Field(default=512, gt=0)
    fit_mode: Literal["fit", "fill"] = "fill"
    format: Literal["png", "webp", "jpeg"] = "webp"
    compression: Literal["lossless", "balanced", "smallest"] = "balanced"
    max_kb: Optional[int] = Field(default=None, gt=0)
    background_color: str = "#FFFFFF"

    @model_validator(mode="after")
    def check_format(self):
        if self.format == "jpeg" and self.compression == "lossless":
            raise ValueError("JPEG does not support lossless compression")
        return self

class AssetJobBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str = "READY"  # READY, QUEUED, GENERATING, POSTPROCESSING, COMPLETED, FAILED, SKIPPED
    error: Optional[str] = None
    target_width: int = Field(gt=0)
    target_height: int = Field(gt=0)
    output_format: Literal["png", "webp", "jpeg"] = "webp"
    compression_mode: Literal["lossless", "balanced", "smallest"] = "balanced"
    fit_mode: Literal["fit", "fill"] = "fill"
    max_kb: Optional[int] = Field(default=None, gt=0)
    background_color: str = "#FFFFFF"
    selected_revision_id: Optional[str] = None
    output_filename: Optional[str] = None
    attempts: List[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_output(self):
        if self.output_format == "jpeg" and self.compression_mode == "lossless":
            raise ValueError("JPEG does not support lossless compression")
        return self

class TextAssetJob(AssetJobBase):
    ratio: Optional[str] = None
    prompt: str
    style_prompt: Optional[str] = None
    seed: int = -1

class Revision(BaseModel):
    revision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_job_id: str
    image_path: str
    seed: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    width: int
    height: int
    file_size: int
    warnings: List[str] = Field(default_factory=list)

class ExportRecord(BaseModel):
    export_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assets: List[str] # List of revision IDs
