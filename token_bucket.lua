-- Token Bucket Rate Limiter
-- KEYS[1] = Redis key
-- ARGV[1] = capacity
-- ARGV[2] = refill_rate (tokens per second)
-- ARGV[3] = current timestamp (seconds)

local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Read current state
local data = redis.call("HMGET", key, "tokens", "last_refill_ts")

local tokens = tonumber(data[1])
local last_refill_ts = tonumber(data[2])

-- Initialize bucket if it does not exist
if tokens == nil then
    tokens = capacity
    last_refill_ts = now
end

-- Refill tokens based on elapsed time
local elapsed = now - last_refill_ts
if elapsed > 0 then
    local refill = elapsed * refill_rate
    tokens = math.min(capacity, tokens + refill)
    last_refill_ts = now
end

local allowed = 0

-- Consume token if possible
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

-- Persist updated state
redis.call("HMSET", key,
    "tokens", tokens,
    "last_refill_ts", last_refill_ts
)

-- Optional: set TTL so idle buckets expire
redis.call("EXPIRE", key, math.ceil(capacity / refill_rate))

return allowed
