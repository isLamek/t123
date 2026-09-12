"""
Omugongo morning sweep — headless entrypoint run by Windows Task Scheduler.

Usage:
    python run_sweep.py

Logs to data/sweep.log (and stdout). Safe to run manually any time.
"""
from __future__ import annotations

import sys
from datetime import datetime

# Make console output UTF-8 safe on Windows (avoids cp1252 crashes on emoji).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

import config
from omugongo import pipeline


def _log(msg: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    try:
        with open(config.LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def main() -> int:
    _log("=== Omugongo sweep starting ===")
    try:
        pipeline.run_sweep(logger=_log)
        _log("=== Omugongo sweep finished ===")
        return 0
    except Exception as exc:  # noqa: BLE001 — log and exit non-zero for the scheduler
        _log(f"!!! Sweep crashed: {exc!r}")
        import traceback
        _log(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
