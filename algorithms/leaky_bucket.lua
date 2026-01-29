-- KEYS[1] = redis key
-- ARGV[1] = capacity
-- ARGV[2] = outflow_rate (req/sec)
-- ARGV[3] = current timestamp (seconds)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local outflow_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Read current state
local data = redis.call("HMGET", key, "queue", "last_drain_ts")

local queue = tonumber(data[1])
local last_drain_ts = tonumber(data[2])

-- Initialize queue if it does not exist
if queue == nil then
    queue = 0
    last_drain_ts = now
end

-- Drain queue based on elapsed time
local elapsed = now - last_drain_ts
local leaked = elapsed * outflow_rate
queue = math.max(0, queue - leaked)
last_drain_ts = now

-- Add new request to the queue

local allowed = 0
if queue <= capacity then
    queue = queue + 1
    allowed = 1
end

-- Persist updated state
redis.call("HMSET", key,
    "queue", queue,
    "last_drain_ts", last_drain_ts
)      

-- Optional: set TTL so idle queue expire
redis.call("EXPIRE", key, math.ceil(capacity / outflow_rate))   

return {allowed,queue}