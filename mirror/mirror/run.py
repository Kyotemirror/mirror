#!/usr/bin/env python3
import argparse
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Headless Mirror Service")
    p.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Run one update cycle and exit (useful for testing)"
    )
    return p.parse_args()

def main():
    args = parse_args()

    try:
        # Import here so argument parsing errors still work without package import issues
        from .app import MirrorApp
    except Exception as e:
        print(f"ERROR: Unable to import MirrorApp: {e}", file=sys.stderr)
        return 2

    app = MirrorApp(config_path=args.config)

    try:
        if args.once:
            app.run_once()
        else:
            app.run_forever()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        app.shutdown()
    except Exception as e:
        print(f"ERROR: Unhandled exception: {e}", file=sys.stderr)
        try:
            app.shutdown()
        except Exception:
            pass
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
