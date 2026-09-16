from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class Config:
    host: str
    port: int
    evolution_interval_seconds: int
    train_interval_seconds: int
    train_steps_per_cycle: int
    bootstrap_steps: int
    candidates_per_generation: int
    candidate_timeout_seconds: int
    web_max_chars: int
    task_count: int
    random_seed: int
    bootstrap_urls: list
    training: dict
    model: dict
    data: Path = Path("data")
    versions: Path = Path("versions")
    sandbox: Path = Path("sandbox")
    workspace: Path = Path("workspace")
    checkpoints: Path = Path("data/checkpoints")

def load(path="config.json"):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cfg = Config(**{k:v for k,v in raw.items() if k in {
        "host","port","evolution_interval_seconds","train_interval_seconds",
        "train_steps_per_cycle","bootstrap_steps","candidates_per_generation",
        "candidate_timeout_seconds","web_max_chars","task_count","random_seed",
        "bootstrap_urls","training","model"
    }})
    for p in [cfg.data, cfg.versions, cfg.sandbox, cfg.workspace, cfg.checkpoints]:
        p.mkdir(parents=True, exist_ok=True)
    return cfg
