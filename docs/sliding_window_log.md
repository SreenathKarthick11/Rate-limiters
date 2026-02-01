# Sliding Window Log Rate Limiter

## Overview

The **Sliding Window Log** algorithm is a precise rate limiting strategy designed to
solve the **boundary burst problem** found in the Fixed Window Counter approach.

Instead of counting requests in fixed intervals, it tracks the **exact timestamps**
of recent requests and enforces limits over a **rolling time window**.

This guarantees that **no time window of length `W` ever exceeds the request limit**.

It is commonly used in:
- API gateways requiring strict fairness
- Financial or billing-sensitive APIs
- Systems where burst accuracy matters more than memory usage

---

## Core Idea & Properties

- Maintain a **log of request timestamps**
- Log is typically stored in a **Redis Sorted Set**
- Each request:
  - Removes outdated timestamps
  - Adds its own timestamp
  - Checks log size
- Requests are rejected if the log exceeds the limit

| Property | Description |
|--------|------------|
| Window type | Sliding (rolling) |
| Burst handling | Excellent |
| Memory usage | High |
| State | Timestamp log |
| Accuracy | Exact |
| Complexity | Moderate |

---

## Visual Model

Example: **2 requests per minute**

```text
Time →
┌────────────────────────────────────────────┐
│ Sliding window (last 60 seconds)           │
├────────────────────────────────────────────┤
│ 1:00:01 ✓   1:00:30 ✓   1:00:50 ✗          │
└────────────────────────────────────────────┘
````

✔ First 2 requests inside the rolling window are allowed
✗ Any request that causes the count to exceed the limit is rejected

---

## Timeline Example

**Limit:** 2 requests per minute

```text
Time:        1:00:01   1:00:30   1:00:50   1:01:40
Requests:       ✓         ✓         ✗         ✓
Window:     [1:00–2:00 sliding]
```

### Step-by-step

1. **1:00:01**

   * Log = `[1:00:01]`
   * Count = 1 → Allowed

2. **1:00:30**

   * Log = `[1:00:01, 1:00:30]`
   * Count = 2 → Allowed

3. **1:00:50**

   * Log = `[1:00:01, 1:00:30, 1:00:50]`
   * Count = 3 → ❌ Rejected
     *(Timestamp may still remain in the log)*

4. **1:01:40**

   * Window start = `1:00:40`
   * Remove outdated timestamps (`1:00:01`, `1:00:30`)
   * Log = `[1:00:50, 1:01:40]`
   * Count = 2 → Allowed

---

## Algorithm Steps

For each incoming request:

1. Compute the **window start**:

   ```text
   window_start = now - window_size
   ```
2. Remove timestamps older than `window_start`
3. Insert the current request timestamp
4. Count timestamps in the log
5. If count ≤ limit:

   * Allow request
6. Else:

   * Reject request

---

## Mathematical Model

Let:

* `W` = window size (seconds)
* `L` = max requests
* `tᵢ` = timestamps of past requests

A request at time `t` is allowed if:

```text
|{ tᵢ ∈ [t − W, t] }| ≤ L
```

This guarantees strict enforcement across **all rolling windows**.

---

## Pseudocode

```lua
window_start = now - window_size

remove all timestamps < window_start

add now to timestamp_log

if size(timestamp_log) <= limit then
    allowed = true
else
    allowed = false
end

return allowed
```

Atomic execution (e.g., Redis Lua scripts) is required to avoid race conditions.

---

## Comparison with Fixed Window Counter

| Feature         | Fixed Window | Sliding Window Log |
| --------------- | ------------ | ------------------ |
| Window type     | Fixed        | Sliding            |
| Boundary bursts | ❌ Yes        | ✅ No               |
| Accuracy        | Medium       | Exact              |
| Memory usage    | Low          | High               |
| Implementation  | Simple       | Moderate           |

---

## Advantages

* Perfectly enforces rate limits
* No boundary burst problem
* Fair under all traffic patterns
* Works well for critical APIs

---

## Limitations

* High memory usage (stores timestamps)
* Each request requires log maintenance
* Rejected requests may still consume memory
* Less scalable for very high QPS systems

---

## When to Use Sliding Window Log

Sliding Window Log is ideal when:

* Strict rate correctness is required
* Traffic fairness is critical
* Request volume is moderate
* Memory usage is acceptable

Typical use cases:

* Payment APIs
* Authentication systems
* Abuse prevention
* Security-sensitive endpoints

---

## References

* [Rate Limiter – ByteByteGo](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)
* Redis Sorted Sets Documentation

```

---
