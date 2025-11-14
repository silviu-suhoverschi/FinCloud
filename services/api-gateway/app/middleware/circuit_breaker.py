"""
Circuit breaker pattern implementation for API Gateway.
Prevents cascading failures by failing fast when a service is down.
"""

import time
from enum import Enum
from typing import Dict, Optional
from fastapi import HTTPException, status
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast, not calling service
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against failing services.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing recovery, limited requests pass through
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = None,
        recovery_timeout: int = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            service_name: Name of the service being protected
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold or settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.recovery_timeout = recovery_timeout or settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.success_count = 0

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result of function call

        Raises:
            HTTPException: If circuit is open or function fails
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                logger.info(
                    "Circuit breaker transitioning to HALF_OPEN",
                    service=self.service_name
                )
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                logger.warning(
                    "Circuit breaker is OPEN, failing fast",
                    service=self.service_name,
                    time_until_retry=self._time_until_retry()
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service {self.service_name} is currently unavailable. Circuit breaker is OPEN.",
                    headers={"Retry-After": str(int(self._time_until_retry()))}
                )

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            # Require multiple successes to close circuit
            if self.success_count >= 3:
                logger.info(
                    "Circuit breaker closing after successful recovery",
                    service=self.service_name
                )
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Immediately reopen on failure during recovery
            logger.warning(
                "Circuit breaker reopening after failed recovery attempt",
                service=self.service_name
            )
            self.state = CircuitState.OPEN
            self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "Circuit breaker opening due to failures",
                    service=self.service_name,
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold
                )
                self.state = CircuitState.OPEN

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.recovery_timeout

    def _time_until_retry(self) -> float:
        """Calculate seconds until retry is allowed."""
        if self.last_failure_time is None:
            return 0

        time_since_failure = time.time() - self.last_failure_time
        return max(0, self.recovery_timeout - time_since_failure)

    def get_state(self) -> dict:
        """
        Get current circuit breaker state.

        Returns:
            dict: Current state information
        """
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count if self.state == CircuitState.HALF_OPEN else 0,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0,
        }


class CircuitBreakerRegistry:
    """
    Registry to manage multiple circuit breakers for different services.
    """

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service.

        Args:
            service_name: Name of the service

        Returns:
            CircuitBreaker: Circuit breaker instance
        """
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(service_name)
            logger.info("Created circuit breaker", service=service_name)

        return self.breakers[service_name]

    def get_all_states(self) -> Dict[str, dict]:
        """
        Get state of all circuit breakers.

        Returns:
            dict: State of all breakers
        """
        return {
            name: breaker.get_state()
            for name, breaker in self.breakers.items()
        }


# Global circuit breaker registry
circuit_breaker_registry = CircuitBreakerRegistry()
