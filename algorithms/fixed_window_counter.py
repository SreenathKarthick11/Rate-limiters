from time import time
from redis_client import run_fixed_window_counter

def fixed_window_counter_limit(
    *,
    identifier: str,
    capacity: int,
    window_size: int,
) -> tuple[bool, dict]:
    """
    Apply fixed window counter rate limiting.

    identifier   -> user/IP/route key
    capacity     -> max requests allowed in the window
    window_size  -> size of the time window in seconds
    """
    now = int(time())
    redis_key = f"rate:fixed_window_counter:{identifier}"

    allowed,curr_capacity,retry_after = run_fixed_window_counter(
        key=redis_key,
        capacity=capacity,
        window_size=window_size,
        now=now,
    )

    return allowed, {"current": curr_capacity, "retry_after": retry_after}