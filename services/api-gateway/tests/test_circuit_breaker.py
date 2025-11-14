"""
Tests for circuit breaker pattern
"""

import pytest
from app.middleware.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    circuit_breaker_registry,
)


def test_circuit_breaker_initial_state():
    """Test circuit breaker starts in CLOSED state"""
    cb = CircuitBreaker("test-service")
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_successful_call():
    """Test successful call through circuit breaker"""
    cb = CircuitBreaker("test-service", failure_threshold=3)

    def success_func():
        return "success"

    result = cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_failed_call():
    """Test failed call increments failure count"""
    cb = CircuitBreaker("test-service", failure_threshold=3)

    def fail_func():
        raise Exception("Service error")

    # First failure
    with pytest.raises(Exception):
        cb.call(fail_func)

    assert cb.failure_count == 1
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_opens_after_threshold():
    """Test circuit breaker opens after failure threshold"""
    cb = CircuitBreaker("test-service", failure_threshold=3)

    def fail_func():
        raise Exception("Service error")

    # Fail threshold times
    for i in range(3):
        with pytest.raises(Exception):
            cb.call(fail_func)

    # Circuit should now be OPEN
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3


def test_circuit_breaker_fails_fast_when_open():
    """Test circuit breaker fails fast when OPEN"""
    from fastapi import HTTPException

    cb = CircuitBreaker("test-service", failure_threshold=3)

    def fail_func():
        raise Exception("Service error")

    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Next call should fail immediately without calling function
    call_count = [0]

    def count_func():
        call_count[0] += 1
        return "success"

    with pytest.raises(HTTPException) as exc_info:
        cb.call(count_func)

    assert exc_info.value.status_code == 503
    assert "Circuit breaker is OPEN" in exc_info.value.detail
    assert call_count[0] == 0  # Function should not have been called


def test_circuit_breaker_transitions_to_half_open():
    """Test circuit breaker transitions from OPEN to HALF_OPEN after timeout"""
    import time

    cb = CircuitBreaker("test-service", failure_threshold=2, recovery_timeout=1)

    def fail_func():
        raise Exception("Service error")

    # Open the circuit
    for i in range(2):
        with pytest.raises(Exception):
            cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    time.sleep(1.1)

    # Next call should transition to HALF_OPEN
    def success_func():
        return "success"

    result = cb.call(success_func)
    assert result == "success"
    assert cb.success_count == 1


def test_circuit_breaker_closes_after_successful_recovery():
    """Test circuit breaker closes after successful recovery"""
    import time

    cb = CircuitBreaker("test-service", failure_threshold=2, recovery_timeout=1)

    def fail_func():
        raise Exception("Service error")

    # Open the circuit
    for i in range(2):
        with pytest.raises(Exception):
            cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    time.sleep(1.1)

    # Make 3 successful calls to close circuit
    def success_func():
        return "success"

    for i in range(3):
        result = cb.call(success_func)
        assert result == "success"

    # Circuit should be CLOSED
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_reopens_on_failure_during_half_open():
    """Test circuit breaker reopens if failure occurs during HALF_OPEN"""
    import time

    cb = CircuitBreaker("test-service", failure_threshold=2, recovery_timeout=1)

    def fail_func():
        raise Exception("Service error")

    # Open the circuit
    for i in range(2):
        with pytest.raises(Exception):
            cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    time.sleep(1.1)

    # First call succeeds (transitions to HALF_OPEN)
    def success_func():
        return "success"

    cb.call(success_func)

    # Second call fails (should reopen circuit)
    with pytest.raises(Exception):
        cb.call(fail_func)

    assert cb.state == CircuitState.OPEN


def test_circuit_breaker_get_state():
    """Test getting circuit breaker state"""
    cb = CircuitBreaker("test-service")

    state = cb.get_state()
    assert state["service"] == "test-service"
    assert state["state"] == CircuitState.CLOSED.value
    assert state["failure_count"] == 0


def test_circuit_breaker_registry():
    """Test circuit breaker registry"""
    registry = circuit_breaker_registry

    # Get or create breaker
    cb1 = registry.get_breaker("service-1")
    assert cb1.service_name == "service-1"

    # Getting same service returns same instance
    cb2 = registry.get_breaker("service-1")
    assert cb1 is cb2

    # Get all states
    states = registry.get_all_states()
    assert "service-1" in states
    assert states["service-1"]["state"] == CircuitState.CLOSED.value


def test_circuit_breaker_with_args():
    """Test circuit breaker with function arguments"""
    cb = CircuitBreaker("test-service")

    def add(a, b):
        return a + b

    result = cb.call(add, 2, 3)
    assert result == 5


def test_circuit_breaker_with_kwargs():
    """Test circuit breaker with function keyword arguments"""
    cb = CircuitBreaker("test-service")

    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}"

    result = cb.call(greet, name="World", greeting="Hi")
    assert result == "Hi, World"
