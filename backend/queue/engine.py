import asyncio
import logging
from enum import Enum
from typing import List, Callable, Any, Optional, Dict
from dataclasses import dataclass
from collections import deque

class JobStatus(Enum):
    READY = "READY"
    QUEUED = "QUEUED"
    GENERATING = "GENERATING"
    POSTPROCESSING = "POSTPROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    INTERRUPTED = "INTERRUPTED"

@dataclass
class QueueItem:
    job_id: str
    execute_fn: Callable
    status: JobStatus = JobStatus.READY
    error: Optional[str] = None

class GenerationQueue:
    def __init__(self):
        self.queue: deque[QueueItem] = deque()
        self.active_job: Optional[QueueItem] = None
        self.is_running = False
        self._stop_after_current = False
        self._wake: Optional[asyncio.Event] = None
        self._shutdown = False

    def enqueue(self, job_id: str, execute_fn: Callable):
        # Avoid duplicate enqueue
        if (self.active_job and self.active_job.job_id == job_id) or any(item.job_id == job_id for item in self.queue):
            return False
        self.queue.append(QueueItem(job_id, execute_fn, JobStatus.QUEUED))
        if self._wake is not None:
            self._wake.set()
        return True

    async def run(self):
        self._wake = asyncio.Event()
        self.is_running = True
        while not self._shutdown:
            if not self.queue:
                self._wake.clear()
                if not self.queue and not self._shutdown:
                    await self._wake.wait()
                continue

            item = self.queue.popleft()

            # Check if item was marked as SKIPPED/CANCELLED while in queue
            if item.status == JobStatus.SKIPPED:
                continue

            self.active_job = item
            item.status = JobStatus.GENERATING

            try:
                await item.execute_fn()
                item.status = JobStatus.COMPLETED
            except Exception as e:
                item.status = JobStatus.FAILED
                item.error = str(e)
            finally:
                self.active_job = None

            if self._stop_after_current:
                self.cancel_all_pending()
                self._stop_after_current = False

        self.is_running = False

    def shutdown(self):
        self._shutdown = True
        if self._wake is not None:
            self._wake.set()

    def cancel_job(self, job_id: str):
        # Cancel if in queue
        for item in self.queue:
            if item.job_id == job_id:
                item.status = JobStatus.SKIPPED
                return True
        return False

    def cancel_all_pending(self):
        for item in self.queue:
            item.status = JobStatus.SKIPPED

    def stop_after_current(self):
        self._stop_after_current = True

    def is_queued(self, job_id: str) -> bool:
        """Return True when job_id is pending or is the active job."""
        if self.active_job and self.active_job.job_id == job_id:
            return True
        return any(item.job_id == job_id for item in self.queue)
