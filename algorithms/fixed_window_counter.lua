-- KEYS[1] = redis key (includes window id)
-- ARGV[1] = limit
-- ARGV[2] = window_size (seconds)
-- ARGV[3] = now (epoch seconds)

local limit = tonumber(ARGV[1])
local window_size = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Increment counter
local current = redis.call("INCR", KEYS[1])

-- Set expiry on first request
if current == 1 then
    redis.call("EXPIRE", KEYS[1], window_size)
end

if current <= limit then
    return {1, current, 0}  -- allowed, retry_after = 0
else
    -- Compute window end
    local window_start = now - (now % window_size)
    local window_end = window_start + window_size
    local retry_after = window_end - now

    return {0, current, retry_after}
end
