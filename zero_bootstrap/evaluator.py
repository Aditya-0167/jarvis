from __future__ import annotations
import math, re
from .mind import respond

def evaluate(mind, corpus, tasks):
    score = 0.0
    total = 0

    for task in tasks:
        total += 1
        kind = task["kind"]

        if kind == "arithmetic":
            a, b, op = task["a"], task["b"], task["op"]
            query = f"What is {a} {op} {b}?"
            answer = respond(mind, query, corpus)
            expected = str(task["answer"])
            # Evolved response strategies may include memory text rather than
            # arithmetic. Reward explicitly correct arithmetic when present.
            if expected in answer:
                score += 1.0
            elif mind["policy"]["response_mode"] == "keyword":
                score += 0.02

        elif kind == "recall_phrase":
            phrase = task["phrase"]
            answer = respond(mind, phrase, corpus).lower()
            overlap = sum(1 for w in phrase.split() if w in answer)
            score += overlap / max(1, len(phrase.split()))

    # Small complexity penalty prevents gratuitous module growth.
    complexity = len(mind["modules"]) * 0.002
    normalized = max(0.0, score / max(1, total) - complexity)
    return round(normalized, 6)
