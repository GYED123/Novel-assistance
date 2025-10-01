from __future__ import annotations
import os, re, yaml, json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent
STORY_DIR = ROOT / "story"
SCENES_DIR = STORY_DIR / "scenes"
PROMPTS_DIR = ROOT / "prompts"

def ensure_dirs():
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists(): return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def dump_yaml(path: Path, data: Dict[str, Any]):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def read_prompt(name: str) -> str:
    with open(PROMPTS_DIR / f"{name}.txt", "r", encoding="utf-8") as f:
        return f.read()

def next_scene_path(index: int | None = None) -> Path:
    ensure_dirs()
    if index is None:
        # 自动递增
        existing = sorted(SCENES_DIR.glob("scene_*.md"))
        idx = len(existing) + 1
    else:
        idx = index
    return SCENES_DIR / f"scene_{idx:03d}.md"
