from __future__ import annotations

import json
import hashlib
from pathlib import Path
import torch

from .model import build_model

class Storage:
    def __init__(self, cfg):
        self.cfg = cfg
        self.state_file = cfg.data / "state.json"
        self.corpus = cfg.data / "corpus.txt"

    def ensure_seed(self):
        if not self.state_file.exists():
            model = build_model(self.cfg.model)
            state = {
                "generation": 0,
                "best_score": None,
                "training_steps": 0,
                "parameter_count": sum(p.numel() for p in model.parameters()),
                "created": True,
            }
            torch.save(
                {"model": model.state_dict(), "config": self.cfg.model},
                self.checkpoint_path(0)
            )
            self.save_state(state)

        if not self.corpus.exists():
            self.corpus.write_text(
                "ZERO begins as a tiny randomly initialized computational system.\n",
                encoding="utf-8"
            )

    def save_state(self, state):
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def load_state(self):
        self.ensure_seed()
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def checkpoint_path(self, generation):
        return self.cfg.checkpoints / f"generation_{int(generation):06d}.pt"

    def latest_checkpoint(self):
        self.ensure_seed()
        paths = sorted(self.cfg.checkpoints.glob("generation_*.pt"))
        return paths[-1]

    def workspace_hash(self):
        h = hashlib.sha256()
        if not self.cfg.workspace.exists():
            return h.hexdigest()
        for p in sorted(self.cfg.workspace.rglob("*")):
            if p.is_file():
                h.update(str(p.relative_to(self.cfg.workspace)).encode())
                h.update(p.read_bytes())
        return h.hexdigest()
