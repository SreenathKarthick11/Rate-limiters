# Token Bucket Rate Limiter

## Overview

The **Token Bucket** algorithm is a rate limiting strategy that controls how frequently
an action can occur while still allowing short bursts of traffic.

Unlike strict per-interval limits, Token Bucket smooths traffic over time while
permitting temporary spikes when capacity is available.

It is widely used in:
- Network traffic shaping
- API rate limiting
- Distributed systems
- Resource access control

---

## Core Idea & Properties

- A bucket holds a maximum number of tokens (`capacity`)
- Tokens are added to the bucket at a constant rate (`refill rate`)
- Each request consumes **one token**
- If the bucket is empty, the request is rejected

| Property | Description |
|--------|------------|
| Burst support | Allows short bursts up to capacity |
| Average rate | Enforced over time via refill |
| State-based | Depends on token count and time |
| Deterministic | Time-dependent behavior |

---

## Visual Model

```text
        Refill (tokens / second)
              ↓
        ┌─────────────────┐
        │  Token Bucket   │  Capacity = 5
        │                 │
        │   ● ● ● ● ●     │  ← tokens
        │                 │
        └─────────────────┘
               ↑
         Each request
         consumes 1 token
````

---

### Timeline Example

```
Time (s):     0   1   2   3
Tokens:       5 → 4 → 3 → 2
Requests:     ↑   ↑   ↑
```

If tokens reach **0**, incoming requests are rejected until tokens are refilled.

---

## Algorithm Steps

For each incoming request:

1. Determine the elapsed time since the last refill
    
2. Add tokens based on elapsed time and refill rate
    
3. Cap the token count at the bucket capacity
    
4. If at least one token is available:
    
    - consume one token
        
    - allow the request
        
5. Otherwise:
    
    - reject the request
        
6. Update the bucket state
    

The algorithm relies on **accurate time tracking** and **consistent state updates**.

---

## Mathematical Model

Let:

- `C` = capacity
    
- `R` = refill rate (tokens per second)
    
- `T` = current token count
    
- `Δt` = elapsed time
    

Token refill formula:

```
T = min(C, T + Δt × R)
```

A request is allowed if:

```
T ≥ 1
```

---

## Pseudocode 

```lua
if bucket not initialized:
    tokens = capacity
    last_refill_time = now

elapsed = now - last_refill_time
tokens = min(capacity, tokens + elapsed * refill_rate)

if tokens >= 1 then
    tokens = tokens - 1
    allowed = true
else
    allowed = false
end

last_refill_time = now
return allowed, tokens
```

This pseudocode assumes atomic execution to prevent race conditions.

---

## Retry Semantics

When a request is rejected, the client may be informed how long to wait  
until the next token becomes available.

Example calculation:

```lua
retry_after = ceil((1 - tokens) / refill_rate)
```

This supports predictable and client-friendly throttling behavior.

---

## Advantages

- Allows controlled bursts of traffic
    
- Enforces a smooth long-term rate
    
- Simple and intuitive model
    
- Efficient state representation
    

---

## Limitations

- Time-dependent behavior
    
- Less precise than sliding window algorithms
    
- Requires careful handling of concurrent updates
    

---

## When to Use Token Bucket

Token Bucket is ideal when:

- Occasional bursts are acceptable
    
- Long-term request rate must be controlled
    
- Fairness over time is more important than strict intervals
    

Typical use cases include:

- Public-facing APIs
    
- User-based throttling
    
- Traffic shaping systems

---
## References

- [Rate limiter - Byte Byte Go](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)