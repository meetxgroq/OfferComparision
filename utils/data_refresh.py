"""
Background data refresh foundation for location registry.

Provides a function that can be called to update FX rates, COL indices,
and salary multipliers. Actual data fetching logic is a TODO for future
iteration — this module establishes the interface and startup hook.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

_refresh_thread: Optional[threading.Thread] = None


def refresh_location_data() -> None:
    """Refresh FX rates, COL indices, and salary multipliers.

    Currently a no-op stub. Future implementation will use web search
    or external APIs to fetch updated data and write into the registry.
    """
    logger.info("data_refresh: refresh_location_data called (stub — no-op)")


def start_background_refresh(interval_seconds: int = 86400) -> None:
    """Start a daemon thread that calls refresh_location_data on an interval."""
    global _refresh_thread
    if _refresh_thread is not None and _refresh_thread.is_alive():
        logger.info("data_refresh: background thread already running")
        return

    def _loop() -> None:
        import time
        while True:
            time.sleep(interval_seconds)
            try:
                refresh_location_data()
            except Exception:
                logger.exception("data_refresh: refresh failed")

    _refresh_thread = threading.Thread(target=_loop, daemon=True, name="data-refresh")
    _refresh_thread.start()
    logger.info("data_refresh: background refresh thread started (interval=%ds)", interval_seconds)
