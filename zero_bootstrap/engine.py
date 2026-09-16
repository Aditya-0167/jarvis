from __future__ import annotations

import json
import random
import shutil
import threading
import time
from pathlib import Path

from .memory import Memory
from .mind import DEFAULT_MIND, mutate, inspect, respond
from .tasks import make_tasks
from .evaluator import evaluate
from .bootstrap import bootstrap_corpus
from .trainer import Trainer
from .web import fetch_public


class Engine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.memory = Memory(cfg.data)
        self.stop_event = threading.Event()
        self.trainer = Trainer(cfg)

    @property
    def state_path(self):
        return self.cfg.data / "state.json"

    @property
    def mind_path(self):
        return self.cfg.workspace / "mind.json"

    def initialize(self):
        self.cfg.workspace.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.state_path.write_text(json.dumps({
                "generation": 0,
                "best_score": None,
                "training_steps": 0,
                "created": time.time(),
                "bootstrapped": False,
            }, indent=2), encoding="utf-8")
        if not self.mind_path.exists():
            self.mind_path.write_text(json.dumps(DEFAULT_MIND, indent=2), encoding="utf-8")

    def state(self):
        self.initialize()
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def mind(self):
        self.initialize()
        return json.loads(self.mind_path.read_text(encoding="utf-8"))

    def bootstrap(self):
        self.initialize()
        state = self.state()
        if not state.get("bootstrapped"):
            added = bootstrap_corpus(self.cfg)
            # This is the initial supervised/self-supervised foundation stage.
            result = self.trainer.train(self.cfg.bootstrap_steps)
            state["bootstrapped"] = True
            state["initial_training"] = result
            self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            self.memory.add("bootstrap", json.dumps(result))
            return {"web_chars_added": added, **result}
        return {"status": "already_bootstrapped"}

    def ingest_url(self, url):
        text = fetch_public(url, self.cfg.web_max_chars)
        self.memory.add_text(text, url)
        return {"url": url, "characters": len(text)}

    def ingest_file(self, path):
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
        self.memory.add_text(text, str(path))
        return {"file": str(path), "characters": len(text)}

    def chat(self, text):
        corpus = (self.cfg.data / "corpus.txt").read_text(
            encoding="utf-8", errors="ignore"
        )
        answer = respond(self.mind(), text, corpus)
        self.memory.add("user", text)
        self.memory.add("assistant", answer)
        return answer

    def evolve_once(self):
        self.initialize()
        rng = random.Random(self.cfg.random_seed + self.state()["generation"])
        current = self.mind()
        corpus = (self.cfg.data / "corpus.txt").read_text(
            encoding="utf-8", errors="ignore"
        )
        tasks = make_tasks(
            corpus,
            self.cfg.task_count,
            self.cfg.random_seed + self.state()["generation"],
        )
        base_score = evaluate(current, corpus, tasks)

        candidates = []
        for i in range(self.cfg.candidates_per_generation):
            cand = mutate(current, rng)
            candidates.append((evaluate(cand, corpus, tasks), i, cand))
        candidates.sort(key=lambda x: x[0], reverse=True)

        best_score, _, best = candidates[0]
        accepted = best_score > base_score
        gen = self.state()["generation"] + 1

        version_dir = self.cfg.versions / f"generation_{gen:06d}"
        if version_dir.exists():
            shutil.rmtree(version_dir)
        version_dir.mkdir(parents=True)

        chosen = best if accepted else current
        self.mind_path.write_text(json.dumps(chosen, indent=2), encoding="utf-8")
        (version_dir / "mind.json").write_text(json.dumps(chosen, indent=2), encoding="utf-8")

        result = {
            "generation": gen,
            "base_score": base_score,
            "candidate_scores": [x[0] for x in candidates],
            "accepted": accepted,
            "score": best_score if accepted else base_score,
            "mind": inspect(chosen),
            "time": time.time()
        }
        (version_dir / "result.json").write_text(
            json.dumps(result, indent=2),
            encoding="utf-8"
        )

        state = self.state()
        state["generation"] = gen
        state["best_score"] = result["score"]
        state["last_result"] = result
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self.memory.add("evolution", json.dumps(result))
        return result

    def start_background(self):
        self.initialize()
        self.bootstrap()
        threading.Thread(target=self._background, daemon=True).start()

    def _background(self):
        next_train = time.time()
        next_evolve = time.time()
        while not self.stop_event.is_set():
            now = time.time()
            if now >= next_train:
                try:
                    result = self.trainer.train(self.cfg.train_steps_per_cycle)
                    self.memory.add("training", json.dumps(result))
                    print("[ZERO TRAIN]", result)
                except Exception as exc:
                    print("[ZERO TRAIN ERROR]", repr(exc))
                next_train = now + self.cfg.train_interval_seconds

            if now >= next_evolve:
                try:
                    result = self.evolve_once()
                    print("[ZERO EVOLVE]", result)
                except Exception as exc:
                    print("[ZERO EVOLVE ERROR]", repr(exc))
                next_evolve = now + self.cfg.evolution_interval_seconds

            self.stop_event.wait(2)
