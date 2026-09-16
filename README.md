# ZERO BOOTSTRAP — TRAIN FIRST, THEN CONTINUE BY ITSELF

This build matches the updated plan:

1. Start with a tiny from-scratch model.
2. Bootstrap it with public information and an initial training run.
3. After bootstrap, keep training locally from its accumulated corpus.
4. Periodically mutate/evolve its software-level "mind".
5. Keep persistent checkpoints and history.
6. Provide a local chat UI.
7. No Ollama, Claude, GPT, Llama, Qwen, or pretrained weights.

## Reality check

This is a genuine from-scratch experiment, not a hidden frontier model.

A 192-dimension, 4-layer CPU model is tiny compared with modern frontier systems.
Your Ryzen 5 9600X + 32 GB RAM can run it, but training will be CPU-limited.

The bootstrap stage is deliberately explicit because a random network has to
learn from data before it can be useful.

After bootstrap, the user does not need to hand-train each cycle: `run` starts a
background loop that periodically trains from the stored corpus and evolves the
software-level mind.

## Install

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py bootstrap
python main.py run
```

Or just:

```powershell
python main.py run
```

`run` performs bootstrap automatically if it has not happened yet.

Open:

http://127.0.0.1:8765

## Add more knowledge

Public pages:

```powershell
python main.py ingest https://example.com/page
```

Local files:

```powershell
python main.py ingest-file notes.txt
```

Newly added data enters `data/corpus.txt`. Future training cycles can learn from it.

## What becomes autonomous after bootstrap?

The program can automatically:

- continue local training
- keep checkpoints
- mutate its software-level mind
- evaluate candidates
- accept or reject mutations
- preserve generation history
- accumulate memory
- continue running after you stop interacting with the chat UI

The system does NOT automatically acquire unauthorized access to other computers,
steal private information, exploit third-party infrastructure, or propagate itself
on the public Internet.

## Scaling

The first target is a working bootstrap loop.

Once it works, increasing:
- model width
- layers
- context
- corpus size
- training time
- tool quality
- memory mechanisms
- evaluation quality

will matter much more than simply adding more random evolution cycles.

## Important

Do not expect "a few days" to turn a tiny CPU-trained model into something like Claude.
That is not realistic. The value of this project is that the initial model and its
learning loop are yours and local, so you can continuously develop the system
without a hosted AI subscription.
