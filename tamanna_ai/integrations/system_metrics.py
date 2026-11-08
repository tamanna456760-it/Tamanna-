"""Lightweight, dependency-free host resource metrics for Tamanna AI."""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _memory_bytes() -> tuple[int | None, int | None]:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        values: dict[str, int] = {}
        try:
            lines = meminfo.read_text(encoding="ascii").splitlines()
        except OSError:
            lines = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[0].endswith(":"):
                try:
                    values[parts[0][:-1]] = int(parts[1]) * 1024
                except ValueError:
                    continue
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        if total and available is not None:
            return total, max(0, total - available)
    try:
        import psutil  # type: ignore[import-not-found]
        memory = psutil.virtual_memory()
        return int(memory.total), int(memory.used)
    except (ImportError, OSError, AttributeError):
        return None, None


def _cpu_snapshot() -> tuple[int, int] | None:
    stat = Path("/proc/stat")
    if not stat.exists():
        return None
    try:
        fields = stat.read_text(encoding="ascii").splitlines()[0].split()[1:]
        values = [int(value) for value in fields]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return sum(values), idle
    except (OSError, ValueError, IndexError):
        return None


async def _cpu_percent() -> float | None:
    first = _cpu_snapshot()
    if first is None:
        try:
            import psutil  # type: ignore[import-not-found]
            return float(psutil.cpu_percent(interval=0.12))
        except (ImportError, OSError, AttributeError):
            return None
    await asyncio.sleep(0.12)
    second = _cpu_snapshot()
    if second is None:
        return None
    total_delta = second[0] - first[0]
    idle_delta = second[1] - first[1]
    if total_delta <= 0:
        return None
    return round(max(0.0, min(100.0, 100.0 * (1 - idle_delta / total_delta))), 1)


def _gpu_metrics() -> dict[str, Any]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return {"available": False, "vendor": None, "utilization_percent": None,
                "memory_used_mb": None, "memory_total_mb": None, "name": None}
    try:
        result = subprocess.run(
            [executable, "--query-gpu=name,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            check=True, capture_output=True, text=True, timeout=2,
        )
        first = result.stdout.strip().splitlines()[0]
        name, utilization, used, total = [part.strip() for part in first.split(",", 3)]
        return {
            "available": True, "vendor": "NVIDIA", "name": name[:120],
            "utilization_percent": float(utilization),
            "memory_used_mb": int(float(used)),
            "memory_total_mb": int(float(total)),
        }
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return {"available": False, "vendor": "NVIDIA", "utilization_percent": None,
                "memory_used_mb": None, "memory_total_mb": None, "name": None}


async def collect_system_metrics() -> dict[str, Any]:
    """Collect current host CPU, RAM, disk, and optional NVIDIA GPU metrics."""
    cpu = await _cpu_percent()
    memory_total, memory_used = _memory_bytes()
    disk = shutil.disk_usage(Path.cwd())
    return {
        "cpu": {"usage_percent": cpu, "logical_cores": os.cpu_count()},
        "memory": {
            "used_bytes": memory_used, "total_bytes": memory_total,
            "usage_percent": round(memory_used * 100 / memory_total, 1)
            if memory_used is not None and memory_total else None,
        },
        "disk": {
            "used_bytes": disk.used, "total_bytes": disk.total,
            "free_bytes": disk.free,
            "usage_percent": round(disk.used * 100 / disk.total, 1)
            if disk.total else None,
        },
        "gpu": _gpu_metrics(),
    }


__all__ = ["collect_system_metrics"]
