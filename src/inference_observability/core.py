from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class RequestEvent:
    request_id: str
    duration_ms: float
    success: bool
    timestamp: float

    def __post_init__(self):
        if not self.request_id.strip() or self.duration_ms < 0 or self.timestamp < 0:
            raise ValueError("invalid request event")

def percentile(values: list[float], p: float) -> float:
    if not values or not 0 <= p <= 100:
        raise ValueError("non-empty values and percentile in [0, 100] required")
    ordered = sorted(values)
    return ordered[max(0, ceil(p / 100 * len(ordered)) - 1)]

def summarize(events: list[RequestEvent]) -> dict:
    if not events:
        return {"count": 0, "error_rate": 0.0, "mean_ms": 0.0, "p95_ms": 0.0}
    durations = [e.duration_ms for e in events]
    return {"count": len(events), "error_rate": sum(not e.success for e in events)/len(events),
            "mean_ms": sum(durations)/len(durations), "p95_ms": percentile(durations, 95)}

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_successes: int = 2):
        if failure_threshold < 1 or recovery_successes < 1:
            raise ValueError("thresholds must be positive")
        self.failure_threshold, self.recovery_successes = failure_threshold, recovery_successes
        self.state, self.failures, self.successes = "closed", 0, 0

    def failure(self):
        self.failures += 1
        self.successes = 0
        if self.state == "half_open" or self.failures >= self.failure_threshold:
            self.state = "open"
        return self.state

    def probe(self):
        if self.state == "open":
            self.state, self.successes = "half_open", 0
        return self.state

    def success(self):
        if self.state == "half_open":
            self.successes += 1
            if self.successes >= self.recovery_successes:
                self.state, self.failures, self.successes = "closed", 0, 0
        elif self.state == "closed":
            self.failures = 0
        return self.state
