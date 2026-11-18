from inference_observability import RequestEvent, summarize, CircuitBreaker

def test_metrics():
    events = [RequestEvent("a", 10, True, 1), RequestEvent("b", 30, False, 2)]
    result = summarize(events)
    assert result["count"] == 2
    assert result["error_rate"] == .5
    assert result["p95_ms"] == 30

def test_breaker():
    breaker = CircuitBreaker(2, 2)
    breaker.failure()
    assert breaker.failure() == "open"
    breaker.probe()
    breaker.success()
    assert breaker.success() == "closed"
