from pathlib import Path
import json, time

class Memory:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.log = self.root / "experience.jsonl"
        self.corpus = self.root / "corpus.txt"
        if not self.corpus.exists():
            self.corpus.write_text(
                "ZERO begins with a tiny seed. Its knowledge and capabilities must "
                "grow through experience and self-development.\n",
                encoding="utf-8"
            )

    def add(self, kind, value, meta=None):
        item = {"time": time.time(), "kind": kind, "value": value, "meta": meta or {}}
        with self.log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def recent(self, n=30):
        if not self.log.exists():
            return []
        rows = []
        for line in self.log.read_text(encoding="utf-8").splitlines()[-n:]:
            try: rows.append(json.loads(line))
            except: pass
        return rows

    def add_text(self, text, source):
        with self.corpus.open("a", encoding="utf-8") as f:
            f.write(f"\n\n===== {source} =====\n")
            f.write(text)
        self.add("knowledge", source, {"chars": len(text)})
