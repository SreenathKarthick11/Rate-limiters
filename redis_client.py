import redis
from pathlib import Path

# Redis connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Load Lua script
LUA_SCRIPT_PATH = Path(__file__).parent / "token_bucket.lua"

with open(LUA_SCRIPT_PATH, "r") as f:
    TOKEN_BUCKET_LUA = f.read()

# Register script (returns callable object)
token_bucket_script = redis_client.register_script(TOKEN_BUCKET_LUA)


def run_token_bucket(key: str,capacity: int,refill_rate: float,now: int) -> bool:
    """
    Execute token bucket rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    result = token_bucket_script(
        keys=[key],
        args=[capacity, refill_rate, now]
    )

    return result == 1