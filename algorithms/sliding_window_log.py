from time import time
from redis_client import run_sliding_window_log

def sliding_window_log_limit(
    *,
    identifier: str,
    capacity: int,
    window_size: int,
) -> tuple[bool, dict]:
    """
    Apply sliding window log rate limiting.

    identifier   -> user/IP/route key
    capacity     -> max requests allowed in the window
    window_size  -> size of the time window in seconds
    """
    now = int(time()*1000)  # Convert to milliseconds
    redis_key = f"rate:sliding_window_log:{identifier}"

    allowed,curr_capacity,retry_after = run_sliding_window_log(
        key=redis_key,
        capacity=capacity,
        window_size=window_size*1000,  # Convert to milliseconds
        now=now,
    )

    return allowed, {"current": curr_capacity, "retry_after": retry_after}