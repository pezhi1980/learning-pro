# backend/operations/metrics_monitor.py

import time
import math
from typing import Dict, List, Any
from .operational_models import SystemMetric


class MetricsMonitor:
    def __init__(self):
        self._counters: Dict[str, int] = {
            "api_requests_total": 0,
            "api_errors_total": 0,
            "generation_failures_total": 0,
            "validation_failures_total": 0,
            "database_failures_total": 0,
            "speech_tts_failures_total": 0,
            "job_failures_total": 0,
        }
        self._latencies: List[float] = []

    def record_request(self, status_code: int, latency_ms: float):
        self._counters["api_requests_total"] += 1
        if status_code >= 400:
            self._counters["api_errors_total"] += 1
        self._latencies.append(latency_ms)
        if len(self._latencies) > 1000:
            self._latencies.pop(0)

    def record_failure(self, failure_type: str):
        key = f"{failure_type}_failures_total"
        if key in self._counters:
            self._counters[key] += 1
        else:
            self._counters[key] = 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        p95 = 0.0
        if self._latencies:
            sorted_lat = sorted(self._latencies)
            idx = int(math.ceil(0.95 * len(sorted_lat))) - 1
            p95 = sorted_lat[max(0, idx)]

        total_requests = max(1, self._counters["api_requests_total"])
        error_rate = (self._counters["api_errors_total"] / total_requests) * 100

        return {
            "counters": dict(self._counters),
            "p95_latency_ms": round(p95, 2),
            "error_rate_percent": round(error_rate, 2),
            "timestamp": time.time(),
        }
