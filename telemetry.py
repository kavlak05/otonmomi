import os
import platform
from datetime import datetime, timezone
from typing import Any


class TelemetryCollector:
    def collect(self) -> dict[str, Any]:
        load_avg: tuple[float, float, float] | None = None
        if hasattr(os, "getloadavg"):
            try:
                load_avg = os.getloadavg()
            except OSError:
                load_avg = None

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": platform.system(),
            "release": platform.release(),
            "pid": os.getpid(),
            "load_1m": round(load_avg[0], 2) if load_avg else None,
            "cpu_count": os.cpu_count() or 1,
            "mode": "cloud_gemini_autonomous_avatar",
            "status": "healthy",
        }
