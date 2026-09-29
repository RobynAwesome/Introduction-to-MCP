# continuous_gsmb_runner.py
"""
Continuous GSM‑B Proof‑of‑Concept runner.

Keeps the full GSM‑B workflow alive (activation gate → protocol stack → spawn‑swarm validation → telemetry) until the process is stopped.
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# Running this file by path puts its package directory first on sys.path,
# where kopano/logging.py would shadow Python's standard logging module.
_PACKAGE_DIR = Path(__file__).resolve().parent
sys.path[:] = [entry for entry in sys.path if Path(entry or ".").resolve() != _PACKAGE_DIR]
sys.path.insert(0, str(_PACKAGE_DIR.parent))

import logging

from kopano.gsmb_poc import run_gsmb_poc
from kopano.kpgs_renter_entry import assert_and_log_entry

logger = logging.getLogger(__name__)

def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def run_continuous(*, renter_id: str, hood_ack: str, interval_seconds: int = 60) -> None:
    """Execute the GSM‑B POC in a loop.

    Parameters
    ----------
    interval_seconds : int
        Seconds to wait between successive runs. Default = 60 s.
    """
    try:
        assert_and_log_entry(
            renter_id=renter_id,
            operation="cli:continuous_gsmb_runner",
            hood_ack=hood_ack,
        )
    except ValueError as exc:
        logger.error("[ContinuousRunner] BLOCKED before execution: %s", exc)
        return

    logger.info("[ContinuousRunner] START – renter %s, interval %s s", renter_id, interval_seconds)
    iteration = 0
    try:
        while True:
            iteration += 1
            logger.info("[ContinuousRunner] Iteration %d – start %s", iteration, _iso_now())
            try:
                result = run_gsmb_poc()
                logger.info(
                    "[ContinuousRunner] Iteration %d – completed %s – verdict=%s, gate=%s, local_emissions=%s",
                    iteration,
                    _iso_now(),
                    result.get("verdict"),
                    result.get("gate", {}).get("activation_allowed"),
                    result.get("agent_dots_emitted", 0),
                )
                if result.get("verdict") != "PASS":
                    logger.error("[ContinuousRunner] Stopping after non-PASS local receipt")
                    return
            except Exception as exc:
                logger.exception("[ContinuousRunner] Iteration %d – error %s", iteration, exc)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("[ContinuousRunner] STOPPED by user at %s", _iso_now())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renter-id", required=True)
    parser.add_argument("--hood-ack", required=True, help="Exact canonical renter acknowledgement")
    parser.add_argument("--interval-seconds", type=int, default=60)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    )
    run_continuous(
        renter_id=args.renter_id,
        hood_ack=args.hood_ack,
        interval_seconds=args.interval_seconds,
    )
