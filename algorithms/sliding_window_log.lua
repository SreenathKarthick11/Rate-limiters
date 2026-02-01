-- KEYS[1] = Redis key
-- ARGV[1] = current timestamp (ms)
-- ARGV[2] = window size (ms)
-- ARGV[3] = max requests

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

-- Remove outdated timestamps
local window_start = now - window
redis.call("ZREMRANGEBYSCORE", key, 0, window_start)

-- Current request count
local count = redis.call("ZCARD", key)

if count < limit then
    -- Add current request timestamp
    redis.call("ZADD", key, now, now)

    -- Set TTL slightly larger than window
    redis.call("PEXPIRE", key, window)

    return {1,count, 0}  -- allowed, retry_after = 0
else
    -- Oldest request timestamp
    local oldest = redis.call("ZRANGE", key, 0, 0, "WITHSCORES")
    local retry_after = window - (now - tonumber(oldest[2]))

    return {0,count,retry_after}
end
