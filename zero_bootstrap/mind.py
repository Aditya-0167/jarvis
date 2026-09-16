from __future__ import annotations
import copy, random

DEFAULT_MIND = {
    "modules": [
        {"name": "novelty", "kind": "score", "weights": {"new_chars": 1.0, "repeat_penalty": 0.25}},
        {"name": "length_control", "kind": "score", "weights": {"short": 0.2, "medium": 0.8, "long": 0.2}},
        {"name": "recall", "kind": "memory", "capacity": 16},
    ],
    "policy": {
        "response_mode": "extractive",
        "memory_threshold": 0.5
    }
}

def clone(mind):
    return copy.deepcopy(mind)

def mutate(mind, rng=None):
    rng = rng or random.Random()
    out = clone(mind)

    choices = ["add_module", "remove_module", "change_weight", "change_capacity", "change_mode"]
    action = rng.choice(choices)

    if action == "add_module":
        names = {"novelty","length_control","recall","pattern","compression","question_focus","source_mix"}
        existing = {m["name"] for m in out["modules"]}
        available = list(names - existing)
        if available:
            name = rng.choice(available)
            if name in ("recall",):
                out["modules"].append({"name": name, "kind": "memory", "capacity": rng.randint(8, 64)})
            else:
                out["modules"].append({"name": name, "kind": "score", "weights": {"primary": rng.uniform(0.1, 2.0)}})

    elif action == "remove_module" and len(out["modules"]) > 1:
        idx = rng.randrange(len(out["modules"]))
        out["modules"].pop(idx)

    elif action == "change_weight":
        score_modules = [m for m in out["modules"] if m.get("kind") == "score"]
        if score_modules:
            mod = rng.choice(score_modules)
            key = rng.choice(list(mod["weights"].keys()))
            mod["weights"][key] = round(max(0.0, min(3.0, mod["weights"][key] + rng.uniform(-0.5, 0.5))), 3)

    elif action == "change_capacity":
        mems = [m for m in out["modules"] if m.get("kind") == "memory"]
        if mems:
            mems[0]["capacity"] = rng.randint(4, 128)

    elif action == "change_mode":
        out["policy"]["response_mode"] = rng.choice(["extractive", "summarize", "keyword", "memory_first"])

    return out

def inspect(mind):
    return {
        "module_count": len(mind["modules"]),
        "modules": [m["name"] for m in mind["modules"]],
        "policy": mind["policy"],
    }

def respond(mind, user_text, corpus):
    # This is intentionally simple: the seed can already converse, but not
    # like a pretrained LLM. Evolution changes the response strategy.
    mode = mind["policy"]["response_mode"]
    words = [w for w in user_text.lower().split() if w.isalpha()]
    corpus_lines = [x.strip() for x in corpus.splitlines() if x.strip()]
    hits = []

    for line in corpus_lines:
        low = line.lower()
        score = sum(1 for w in words if len(w) > 2 and w in low)
        if score:
            hits.append((score, line))

    hits.sort(reverse=True)
    top = [line for _, line in hits[:5]]

    if mode == "keyword":
        return "Keywords: " + ", ".join(words[:12])

    if top:
        return "Relevant memory:\n" + "\n".join(top[:3])

    if mode == "memory_first":
        return "I don't have a strong matching memory yet. I can store this conversation and keep developing."

    return "I don't know that yet. I am a from-scratch system and this generation is still developing."
