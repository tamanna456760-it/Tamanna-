"""Shim module to expose the implementation located under IT/bd-king-r7/sync

Tests and some scripts import bd-king-r7/sync/bd-king-r7_max_sync.py. The
implementation lives under IT/bd-king-r7/sync for legacy layout; this shim
loads that module and re-exports its public symbols.
"""

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
impl_path = ROOT / "IT" / "bd-king-r7" / "sync" / "bd-king-r7_max_sync.py"
spec = importlib.util.spec_from_file_location("bdking_impl", str(impl_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Re-export public symbols
for _name, _val in module.__dict__.items():
    if not _name.startswith("_"):
        globals()[_name] = _val
