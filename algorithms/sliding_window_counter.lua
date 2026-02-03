-- KEYS[1] = base redis key (e.g., rate:sliding_window_counter:<id>)
-- ARGV[1] = limit
-- ARGV[2] = window_size (seconds)
-- ARGV[3] = now (epoch seconds)

local limit = tonumber(ARGV[1])
local window_size = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Calculate current window start
local current_window_start = now - (now % window_size)
local prev_window_start = current_window_start - window_size

-- Redis keys
local current_key = KEYS[1] .. ":" .. current_window_start
local prev_key = KEYS[1] .. ":" .. prev_window_start

-- Get counts
local current_count = tonumber(redis.call("GET", current_key)) or 0
local prev_count = tonumber(redis.call("GET", prev_key)) or 0

-- How far we are into the current window
local elapsed = now - current_window_start
local weight = 1 - (elapsed / window_size)

-- Sliding window estimate
local effective_count = current_count + (prev_count * weight)

if effective_count < limit then
    -- Allow request
    current_count = redis.call("INCR", current_key)

    -- Set expiry so old windows disappear automatically
    redis.call("EXPIRE", current_key, window_size * 2)

    return {1, math.floor(effective_count), 0}
else
    -- Retry after next window
    local retry_after = window_size - elapsed
    return {0, math.floor(effective_count), retry_after}
end
