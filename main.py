from zero_bootstrap.config import load
from zero_bootstrap.engine import Engine
from zero_bootstrap.server import make_server

def main():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("run")
    sub.add_parser("evolve")
    tc = sub.add_parser("train-cloud")
    tc.add_argument("--steps", type=int, default=500)
    sub.add_parser("bootstrap")
    w = sub.add_parser("ingest")
    w.add_argument("url")
    f = sub.add_parser("ingest-file")
    f.add_argument("path")
    args = parser.parse_args()

    cfg = load()
    engine = Engine(cfg)

    if args.cmd == "init":
        engine.initialize()
        print("ZERO BOOTSTRAP initialized.")
    elif args.cmd == "bootstrap":
        print(engine.bootstrap())
    elif args.cmd == "evolve":
        print(engine.evolve_once())
    elif args.cmd == "train-cloud":
        engine.initialize()
        print(engine.trainer.train(args.steps))
    elif args.cmd == "ingest":
        print(engine.ingest_url(args.url))
    elif args.cmd == "ingest-file":
        print(engine.ingest_file(args.path))
    elif args.cmd == "run":
        engine.initialize()
        app = make_server(engine)
        engine.start_background()
        print(f"ZERO running at http://{cfg.host}:{cfg.port}")
        app.run(host=cfg.host, port=cfg.port, threaded=True)

if __name__ == "__main__":
    main()
