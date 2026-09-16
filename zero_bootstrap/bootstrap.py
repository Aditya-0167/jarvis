from __future__ import annotations

from pathlib import Path
import time

from .web import fetch_public

def bootstrap_corpus(cfg):
    existing = (cfg.data / "corpus.txt").read_text(
        encoding="utf-8", errors="ignore"
    ) if (cfg.data / "corpus.txt").exists() else ""

    added = 0
    seen = {line for line in existing.splitlines() if line.startswith("===== SOURCE:")}
    for url in cfg.bootstrap_urls:
        marker = f"===== SOURCE: {url} ====="
        if marker in seen:
            continue
        try:
            text = fetch_public(url, cfg.web_max_chars)
            with (cfg.data / "corpus.txt").open("a", encoding="utf-8") as f:
                f.write(f"\n\n{marker}\n{text}\n")
            added += len(text)
            time.sleep(0.5)
        except Exception as exc:
            print("[ZERO WEB]", url, repr(exc))
    return added
