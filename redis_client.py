import redis
from pathlib import Path

# Redis connection
redis_client = redis.Redis(
    host="redis",    # localhost
    port=6379,
    decode_responses=True
)

# Load Lua scripts
LUA_SCRIPT_PATH_TB = Path(__file__).parent / "algorithms" / "token_bucket.lua"
LUA_SCRIPT_PATH_LB = Path(__file__).parent / "algorithms" / "leaky_bucket.lua"


with open(LUA_SCRIPT_PATH_TB, "r") as f:
    TOKEN_BUCKET_LUA = f.read()

with open(LUA_SCRIPT_PATH_LB, "r") as f:
    LEAKY_BUCKET_LUA = f.read()

# Register script (returns callable object)
token_bucket_script = redis_client.register_script(TOKEN_BUCKET_LUA)
leaky_bucket_script = redis_client.register_script(LEAKY_BUCKET_LUA)


def run_token_bucket(key: str,capacity: int,refill_rate: float,now: int) -> bool:
    """
    Execute token bucket rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    allowed,remaining,retry_after = token_bucket_script(
        keys=[key],
        args=[capacity, refill_rate, now]
    )

    return (allowed == 1),remaining,retry_after


def run_leaky_bucket(key: str,capacity: int,outflow_rate: float,now: int) -> bool:
    """
    Execute leaky bucket rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    allowed,curr_capacity = leaky_bucket_script(
        keys=[key],
        args=[capacity, outflow_rate, now]
    )

    return (allowed == 1),curr_capacity