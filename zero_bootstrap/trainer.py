from __future__ import annotations

import time
from pathlib import Path

import torch

from .dataset import ByteDataset
from .model import build_model
from .storage import Storage


class Trainer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.storage = Storage(cfg)
        torch.set_num_threads(max(1, min(torch.get_num_threads(), 12)))

    def _load(self):
        path = self.storage.latest_checkpoint()
        package = torch.load(path, map_location="cpu", weights_only=False)
        model = build_model(package["config"])
        model.load_state_dict(package["model"])
        return model, package["config"]

    def _eval(self, model, dataset, batches=8):
        model.eval()
        losses = []
        with torch.no_grad():
            for _ in range(batches):
                x, y = dataset.batch(self.cfg.training["batch_size"])
                _, loss = model(x, y)
                losses.append(float(loss))
        return sum(losses) / len(losses)

    def train(self, steps):
        model, model_cfg = self._load()
        dataset = ByteDataset(
            self.cfg.data / "corpus.txt",
            model_cfg["block_size"],
        )
        opt = torch.optim.AdamW(
            model.parameters(),
            lr=float(self.cfg.training["learning_rate"]),
            weight_decay=float(self.cfg.training["weight_decay"]),
        )

        before = self._eval(model, dataset)
        started = time.time()
        model.train()

        for _ in range(int(steps)):
            x, y = dataset.batch(self.cfg.training["batch_size"])
            _, loss = model(x, y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                float(self.cfg.training["gradient_clip"]),
            )
            opt.step()

        after = self._eval(model, dataset)

        state = self.storage.load_state()
        state["training_steps"] = int(state.get("training_steps", 0)) + int(steps)
        state["last_train_loss_before"] = before
        state["last_train_loss_after"] = after

        # Keep a durable checkpoint after every training cycle.
        torch.save(
            {"model": model.state_dict(), "config": model_cfg},
            self.storage.checkpoint_path(int(state["generation"])),
        )
        self.storage.save_state(state)

        return {
            "steps": int(steps),
            "loss_before": before,
            "loss_after": after,
            "seconds": time.time() - started,
            "parameters": sum(p.numel() for p in model.parameters()),
        }
