import redis
from pathlib import Path

# Redis connection
redis_client = redis.Redis(
    host="redis",   
    # host="localhost", # For local testing
    port=6379,
    decode_responses=True
)

# Load Lua scripts
LUA_SCRIPT_PATH_TB = Path(__file__).parent / "algorithms" / "token_bucket.lua"
LUA_SCRIPT_PATH_LB = Path(__file__).parent / "algorithms" / "leaky_bucket.lua"
LUA_SCRIPT_PATH_FWC = Path(__file__).parent / "algorithms" / "fixed_window_counter.lua"
LUA_SCRIPT_PATH_SWL = Path(__file__).parent / "algorithms" / "sliding_window_log.lua"
LUA_SCRIPT_PATH_SWC = Path(__file__).parent / "algorithms" / "sliding_window_counter.lua"

with open(LUA_SCRIPT_PATH_TB, "r") as f:
    TOKEN_BUCKET_LUA = f.read()

with open(LUA_SCRIPT_PATH_LB, "r") as f:
    LEAKY_BUCKET_LUA = f.read()

with open(LUA_SCRIPT_PATH_SWL, "r") as f:
    SLIDING_WINDOW_LOG_LUA = f.read()

with open(LUA_SCRIPT_PATH_FWC, "r") as f:
    FIXED_WINDOW_COUNTER_LUA = f.read()

with open(LUA_SCRIPT_PATH_SWC, "r") as f:
    SLIDING_WINDOW_COUNTER_LUA = f.read()

# Register script (returns callable object)
token_bucket_script = redis_client.register_script(TOKEN_BUCKET_LUA)
leaky_bucket_script = redis_client.register_script(LEAKY_BUCKET_LUA)
fixed_window_counter_script = redis_client.register_script(FIXED_WINDOW_COUNTER_LUA)
sliding_window_counter_script = redis_client.register_script(SLIDING_WINDOW_COUNTER_LUA)
sliding_window_log_script = redis_client.register_script(SLIDING_WINDOW_LOG_LUA)

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


def run_fixed_window_counter(key: str,capacity: int,window_size: int,now: int) -> bool:
    """
    Execute fixed window counter rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    allowed,curr_capacity,retry_after = fixed_window_counter_script(
        keys=[key],
        args=[capacity, window_size, now]
    )
    
    return (allowed == 1),curr_capacity,retry_after


def run_sliding_window_log(key: str,capacity: int,window_size: int,now: int) -> bool:
    """
    Execute sliding window log rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    allowed,curr_capacity,retry_after = sliding_window_log_script(
        keys=[key],
        args=[capacity, window_size, now]
    )

    return (allowed == 1),curr_capacity,retry_after

def run_sliding_window_counter(key: str,capacity: int,window_size: int,now: int) -> bool:
    """
    Execute sliding window counter rate limiter.

    Returns:
        True  -> request allowed
        False -> request denied
    """
    allowed,curr_capacity,retry_after = sliding_window_counter_script(
        keys=[key],
        args=[capacity, window_size, now]
    )

    return (allowed == 1),curr_capacity,retry_after

