-- KEYS[1] = Redis key
-- ARGV[1] = limit
-- ARGV[2] = window_size (seconds)
-- ARGV[3] = now (epoch seconds)

local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])


-- Remove outdated timestamps
local window_start = now - window
redis.call("ZREMRANGEBYSCORE", key, 0, window_start)

-- Add current request (unique member)
local member = now .. "-" .. redis.call("INCR", key .. ":seq")
redis.call("ZADD", key, now, member)

-- Set TTL to clean up idle keys
redis.call("PEXPIRE", key, window)
redis.call("PEXPIRE", key .. ":seq", window)

-- Count requests in window AFTER insert
local count = redis.call("ZCARD", key)

if count <= limit then
    return {1, count, 0}
else
    -- Reject: remove the request we just added
    redis.call("ZREM", key, member)

    -- Compute retry-after using oldest request
    local oldest = redis.call("ZRANGE", key, 0, 0, "WITHSCORES")
    local retry_after = window - (now - tonumber(oldest[2]))

    if retry_after < 0 then
        retry_after = 0
    end

    return {0, count - 1, retry_after}
end
