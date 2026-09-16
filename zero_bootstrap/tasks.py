from __future__ import annotations
import random, math

def make_tasks(corpus_text: str, count=32, seed=42):
    rng = random.Random(seed)
    tokens = [x.strip(".,!?;:()[]{}\"'").lower() for x in corpus_text.split()]
    tokens = [x for x in tokens if x]
    tasks = []

    # Generic tasks whose answers can be measured without a pretrained model.
    tasks.extend([
        {"kind": "arithmetic", "a": a, "b": b, "op": "+", "answer": a+b}
        for a,b in [(rng.randint(1,20), rng.randint(1,20)) for _ in range(max(4, count//4))]
    ])
    tasks.extend([
        {"kind": "arithmetic", "a": a, "b": b, "op": "*", "answer": a*b}
        for a,b in [(rng.randint(1,10), rng.randint(1,10)) for _ in range(max(4, count//4))]
    ])

    # Text retrieval tasks are held out from training by selecting snippets
    # from different positions in the corpus.
    if len(tokens) >= 20:
        for _ in range(max(4, count//2)):
            idx = rng.randrange(0, len(tokens)-5)
            phrase = " ".join(tokens[idx:idx+5])
            tasks.append({"kind": "recall_phrase", "phrase": phrase})

    return tasks[:count]
