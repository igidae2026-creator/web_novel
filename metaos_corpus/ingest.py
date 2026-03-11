from __future__ import annotations
import os, zipfile, shutil
from engine.safe_io import safe_copy_bytes
from pathlib import Path
from typing import List, Iterator, Tuple, Optional

TEXT_EXTS = {".txt", ".md", ".csv", ".log"}

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def safe_extract_zip(zip_path: str, out_dir: str) -> List[str]:
    extracted = []
    ensure_dir(out_dir)
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            name = member.filename
            if name.endswith("/") or name.endswith("\\"):
                continue
            dest = Path(out_dir) / name
            dest_resolved = dest.resolve()
            out_resolved = Path(out_dir).resolve()
            if out_resolved not in dest_resolved.parents and dest_resolved != out_resolved:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member, "r") as src:
                safe_copy_bytes(str(dest), src.read(), safe_mode=False)
            extracted.append(str(dest))
    return extracted

def iter_input_files(inputs_dir: str) -> Iterator[str]:
    for root, _, files in os.walk(inputs_dir):
        for fn in files:
            p = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS or ext == ".zip":
                yield p

def read_text(path: str, max_bytes: int = 2_000_000) -> Optional[str]:
    ext = os.path.splitext(path)[1].lower()
    if ext not in {".txt", ".md"}:
        return None
    try:
        with open(path, "rb") as f:
            b = f.read(max_bytes)
        for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
            try:
                return b.decode(enc)
            except Exception:
                continue
        return b.decode("latin1", errors="ignore")
    except Exception:
        return None

def collect_texts(inputs_dir: str, scratch_dir: str) -> List[Tuple[str,str]]:
    ensure_dir(scratch_dir)
    out: List[Tuple[str,str]] = []
    for p in iter_input_files(inputs_dir):
        ext = os.path.splitext(p)[1].lower()
        if ext == ".zip":
            sub = os.path.join(scratch_dir, os.path.splitext(os.path.basename(p))[0])
            files = safe_extract_zip(p, sub)
            for fpath in files:
                t = read_text(fpath)
                if t and t.strip():
                    out.append((fpath, t))
        else:
            t = read_text(p)
            if t and t.strip():
                out.append((p, t))
    return out
