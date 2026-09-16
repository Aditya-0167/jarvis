from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from .trainer import Trainer

class ContinuousTrainer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.stop_event = threading.Event()
        self.trainer = Trainer(cfg)

    def start(self):
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        return thread

    def _loop(self):
        while not self.stop_event.is_set():
            try:
                result = self.trainer.train(
                    int(self.cfg.train_steps_per_cycle)
                )
                print("[ZERO TRAIN]", json.dumps(result))
            except Exception as exc:
                print("[ZERO TRAIN ERROR]", repr(exc))
            self.stop_event.wait(self.cfg.train_interval_seconds)
