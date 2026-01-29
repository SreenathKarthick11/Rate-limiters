from time import time
import math
from redis_client import run_leaky_bucket

def leaky_bucket_limit(
    *,
    identifier: str,
    capacity: int,
    outflow_rate: float,
) -> tuple[bool, dict]:
    """
    Apply leaky bucket rate limiting.

    identifier   -> user/IP/route key
    capacity     -> bucket size
    outflow_rate -> tokens per second
    """

    now = int(time())
    redis_key = f"rate:leaky_bucket:{identifier}"

    allowed,curr_capacity = run_leaky_bucket(
        key=redis_key,
        capacity=capacity,
        outflow_rate=outflow_rate,
        now=now,
    )
    if not allowed:
        retry_after = math.ceil((curr_capacity - capacity + 1) / outflow_rate) if outflow_rate > 0 else None
        return False, {"retry_after": retry_after}

    return allowed, {"curr_capacity": curr_capacity}