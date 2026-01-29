from time import time
from redis_client import run_token_bucket

def token_bucket_limit(
    *,
    identifier: str,
    capacity: int,
    refill_rate: float,
) -> tuple[bool, dict]:
    """
    Apply token bucket rate limiting.

    identifier   -> user/IP/route key
    capacity     -> bucket size
    refill_rate  -> tokens per second
    """

    now = int(time())
    redis_key = f"rate:token_bucket:{identifier}"

    allowed,remaining,retry_after = run_token_bucket(
        key=redis_key,
        capacity=capacity,
        refill_rate=refill_rate,
        now=now,
    )

    return allowed, {"remaining": remaining, "retry_after": retry_after}
