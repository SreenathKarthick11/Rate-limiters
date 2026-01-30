# Leaky Bucket Rate Limiter

## Overview

The **Leaky Bucket** algorithm is a rate limiting strategy that enforces a
**strict, constant output rate** by processing requests in a fixed, steady flow.

Incoming requests are treated like water poured into a bucket with a small hole:
- Requests enter the bucket (queue)
- Requests leave the bucket at a constant rate
- If the bucket overflows, requests are rejected

Unlike Token Bucket, Leaky Bucket **does not allow bursts** and produces
a smooth, predictable request rate.

It is commonly used in:
- Network traffic shaping
- Queue-based throttling systems
- Bandwidth control
- Real-time systems requiring smooth output

---

## Core Idea & Properties

- Requests are added to a queue (bucket)
- The bucket has a fixed capacity
- Requests leak out at a constant rate
- If the bucket is full, new requests are dropped

| Property | Description |
|--------|------------|
| Burst support | ❌ No burst allowance |
| Output rate | Constant and smooth |
| Queue-based | Yes |
| Deterministic | Strict time-based behavior |

---

## Visual Model

```text
        Incoming requests
                ↓
        ┌─────────────────┐
        │   Leaky Bucket  │  Capacity = 5
        │                 │
        │   ■ ■ ■ ■ ■     │  ← queued requests
        │                 │
        └─────────────────┘
                ↓
        Constant leak rate
        (e.g., 1 req/sec)
````

If the bucket is full, incoming requests are **immediately rejected**.

---

## Timeline Example

```
Time (s):      0   1   2   3
Queued:        3 → 3 → 3 → 3
Incoming:      ↑↑  ↑↑  ↑↑
Processed:     ↑   ↑   ↑
```

Even if multiple requests arrive at once, they are **processed one at a time**  
at a fixed rate.

---

## Algorithm Steps

For each incoming request:

1. Check the current queue size
    
2. If the bucket is **not full**:
    
    - enqueue the request
        
3. Otherwise:
    
    - reject the request
        
4. Independently, at fixed intervals:
    
    - dequeue and process requests at the leak rate
        

The processing rate is **independent of arrival rate**.

---

## Mathematical Model

Let:

- `C` = bucket capacity (max queue size)
    
- `L` = leak rate (requests per second)
    
- `Q` = current queue length
    

Request acceptance condition:

```
Q < C
```

Request processing rate:

```
Processed per second = L
```

The system guarantees:

```
Output rate ≤ L
```

---

## Pseudocode

```lua
if queue not initialized:
    queue = empty
    last_leak_time = now

-- Leak phase
elapsed = now - last_leak_time
requests_to_process = floor(elapsed * leak_rate)

for i = 1 to requests_to_process do
    if queue not empty then
        dequeue and process request
    end
end

last_leak_time = now

-- Arrival phase
if queue size < capacity then
    enqueue request
    allowed = true
else
    allowed = false
end

return allowed, queue size
```

This model assumes a background worker or timer to enforce the leak rate.

---

## Retry Semantics

When a request is rejected due to a full bucket, the client may be informed  
how long to wait before retrying.

Example estimation:

```lua
retry_after = ceil(queue_size / leak_rate)
```

This indicates when space is expected to free up in the bucket.

---

## Advantages

- Guarantees a smooth, predictable request rate
    
- Simple conceptual model
    
- Prevents traffic bursts entirely
    
- Well-suited for queue-based systems
    

---

## Limitations

- Does **not allow bursts**
    
- Can introduce latency due to queuing
    
- Requires background processing or timers
    
- Less flexible than Token Bucket
    

---

## When to Use Leaky Bucket

Leaky Bucket is ideal when:

- A **strict output rate** must be enforced
    
- Bursts are undesirable or harmful
    
- Predictable traffic shaping is required
    

Typical use cases include:

- Network bandwidth throttling
    
- Streaming systems
    
- Hardware or I/O rate control
    
- Real-time systems
    

---

## References

- [Rate limiter – ByteByteGo](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)
    
- [RFC 2697 – Single Rate Three Color Marker](https://datatracker.ietf.org/doc/html/rfc2697)
    
