#!/usr/bin/env python3
"""Chạy AssetGen bằng một lệnh: file block -> ảnh đã hậu xử lý. Chỉ dùng thư viện chuẩn.

python3 scripts/assetgen_run.py BLOCKS.txt [--project TÊN] [--out THƯ_MỤC] [--timeout GIÂY]

Tiến độ ra stderr; JSON tóm tắt ra stdout. Mã thoát 0 chỉ khi mọi job COMPLETED.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8001"
TERMINAL = {"COMPLETED", "FAILED"}
# Trạng thái dừng khác COMPLETED/FAILED: không còn tiến triển, coi là thất bại để khỏi chờ vô hạn.
DEAD = {"INTERRUPTED", "SKIPPED", "CANCELLED"}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def request(method, path, data=None, headers=None, timeout=60):
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from None


def post_form(path, fields):
    from urllib.parse import urlencode
    return request("POST", path, urlencode(fields).encode(), {"Content-Type": "application/x-www-form-urlencoded"})


def post_file(path, filename, content):
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: text/plain\r\n\r\n").encode() + content + f"\r\n--{boundary}--\r\n".encode()
    return request("POST", path, body, {"Content-Type": f"multipart/form-data; boundary={boundary}"})


def server_up():
    try:
        request("GET", "/projects/00000000-0000-0000-0000-000000000000", timeout=3)
    except RuntimeError:
        return True  # server trả HTTP lỗi (404) nghĩa là đang chạy
    except OSError:
        return False
    return True


def start_server():
    log_file = tempfile.NamedTemporaryFile(prefix="assetgen_server_", suffix=".log", delete=False)
    log(f"Khởi động server nền, log: {log_file.name}")
    proc = subprocess.Popen([sys.executable, "-m", "backend.api"], cwd=str(ROOT),
                            stdout=log_file, stderr=subprocess.STDOUT, env=os.environ.copy())
    for _ in range(120):
        if proc.poll() is not None:
            raise RuntimeError(f"Server thoát sớm (mã {proc.returncode}); xem log {log_file.name}")
        if server_up():
            return proc
        time.sleep(0.5)
    proc.terminate()
    raise RuntimeError(f"Server không sẵn sàng sau 60 giây; xem log {log_file.name}")


def image_info(path):
    try:
        from PIL import Image
    except ImportError:
        return None, None
    try:
        with Image.open(path) as im:
            has_alpha = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
            return list(im.size), has_alpha
    except Exception:
        return None, None


def run(args):
    blocks = Path(args.blocks)
    content = blocks.read_bytes()
    up = post_file("/batch/upload", blocks.name, content)
    if up["errors"]:
        log("Lỗi parse block, không tạo job:")
        log(json.dumps(up["errors"], ensure_ascii=False, indent=2))
        print(json.dumps({"errors": up["errors"]}, ensure_ascii=False, indent=2))
        return 2
    if not up["jobs"]:
        log("Không có block ASSET nào.")
        return 2
    name = args.project or f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    project = post_form("/projects", {"name": name})
    pid = project.get("id") or project.get("project_id")
    jobs = [{k: v for k, v in j.items() if k != "explicit_fields"} for j in up["jobs"]]
    request("POST", f"/projects/{pid}/batch/jobs", json.dumps(jobs).encode(), {"Content-Type": "application/json"})
    log(f"Project {name} ({pid}), {len(jobs)} job")
    post_form("/batch/generate", {"project_id": pid})

    deadline = time.time() + args.timeout
    last = None
    while True:
        status = request("GET", f"/batch/status?project_id={pid}")
        states = {j["name"]: j["status"] for j in status["jobs"]}
        if states != last:
            log("  " + ", ".join(f"{n}: {s}" for n, s in states.items()))
            last = states
        if all(s in TERMINAL or s in DEAD for s in states.values()):
            break
        if time.time() > deadline:
            log(f"Hết thời gian chờ {args.timeout}s")
            break
        time.sleep(2)

    folder = Path(status["image_folder"])
    out = Path(args.out).resolve() if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    results = []
    for j in status["jobs"]:
        entry = {"name": j["name"], "status": j["status"], "error": j["error"], "file": None,
                 "size_kb": None, "image_size": None, "has_alpha": None}
        if j["status"] == "COMPLETED" and j["output_filename"]:
            src = folder / j["output_filename"]
            if out and src.is_file():
                dst = out / j["output_filename"]
                shutil.copyfile(src, dst)
                src = dst
            if src.is_file():
                entry["file"] = str(src)
                entry["size_kb"] = round(src.stat().st_size / 1024, 2)
                entry["image_size"], entry["has_alpha"] = image_info(src)
        results.append(entry)
    print(json.dumps({"project": name, "project_id": pid, "image_folder": str(folder), "jobs": results},
                     ensure_ascii=False, indent=2))
    return 0 if results and all(r["status"] == "COMPLETED" for r in results) else 1


def main():
    ap = argparse.ArgumentParser(description="AssetGen: file block -> ảnh, một lệnh.")
    ap.add_argument("blocks", help="file chứa các block === ASSET === ... === END ===")
    ap.add_argument("--project", help="tên project (mặc định run-<thời gian>)")
    ap.add_argument("--out", help="thư mục sao chép ảnh hoàn thành")
    ap.add_argument("--timeout", type=int, default=600, help="giây chờ tối đa (mặc định 600)")
    args = ap.parse_args()
    proc = None
    try:
        if server_up():
            log("Dùng server đang chạy ở 127.0.0.1:8001")
        else:
            proc = start_server()
        return run(args)
    except (RuntimeError, OSError) as exc:
        log(f"Lỗi: {exc}")
        return 3
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
