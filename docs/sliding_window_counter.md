# Sliding Window Counter Rate Limiter

## Overview

The **Sliding Window Counter** algorithm is a hybrid rate limiting strategy that
combines ideas from **Fixed Window Counter** and **Sliding Window Log**.

It provides a **smooth approximation of true sliding window rate limiting**
while remaining **memory efficient** and **computationally cheap**.

Instead of tracking every request timestamp, it estimates the request rate
using counters from the **current** and **previous** time windows.

This algorithm is widely used in large-scale systems, including:
- API gateways
- CDN edge rate limiting
- Distributed microservices
- Cloudflare-style traffic throttling

---

## Core Idea & Properties

- Time is divided into **fixed-size windows**
- Maintain two counters:
  - requests in the **current window**
  - requests in the **previous window**
- Requests are evaluated using a **weighted average**
- The weight depends on how far the current time has progressed into the window

| Property | Description |
|--------|------------|
| Window type | Sliding (approximate) |
| Burst handling | Smooths boundary spikes |
| Accuracy | High (approximation) |
| Memory usage | Low (2 counters per key) |
| State | Two counters + time |
| Complexity | O(1) |

---

## Visual Model

Example: **7 requests per minute**

```text
Time →
┌──────────────┬──────────────┐
│ Prev Window  │ Curr Window  │
│   (0–60s)    │  (60–120s)   │
│   5 reqs     │   3 reqs     │
└──────────────┴──────────────┘
        ↑───────────↑
     Sliding window overlaps
     both time windows
````

Instead of a hard reset, the algorithm computes a **weighted contribution**
from the previous window.

---

## Timeline Example

**Limit:** 7 requests / minute

```text
Prev window count     = 5
Current window count  = 3
Elapsed in window     = 30s (50%)
Overlap weight        = 0.5

Effective requests =
    current +
    previous × overlap
= 3 + 5 × 0.5
= 5.5 → 5 (rounded down)
```

Since `5 < 7`, the request is **allowed**.

---

## Algorithm Steps

For each incoming request:

1. Compute the **current window start time**
2. Identify the **previous window**
3. Fetch request counters for both windows
4. Compute how far the current window has progressed
5. Calculate the weighted request count:

   ```
   effective =
       current_count +
       previous_count × overlap_weight
   ```
6. If `effective < limit`:

   * increment current window counter
   * allow the request
7. Otherwise:

   * reject the request
   * return retry time

---

## Mathematical Model

Let:

* `W` = window size (seconds)
* `L` = request limit
* `t` = current timestamp
* `C` = requests in current window
* `P` = requests in previous window

Window boundaries:

```text
current_window_start = t - (t mod W)
elapsed = t - current_window_start
```

Overlap weight:

```text
weight = 1 - (elapsed / W)
```

Effective request count:

```text
effective = C + P × weight
```

Request is allowed if:

```text
effective < L
```

---

## Pseudocode

```lua
current_window = floor(now / window_size)
previous_window = current_window - 1

current_count = counter[current_window]
previous_count = counter[previous_window]

elapsed = now % window_size
weight = 1 - (elapsed / window_size)

effective = current_count + previous_count * weight

if effective < limit then
    counter[current_window] += 1
    allowed = true
else
    allowed = false
end

return allowed
```

This approach assumes **atomic updates** (e.g., Redis + Lua).

---

## Retry Semantics

When a request is rejected, the retry time corresponds to the **end of the
current window**.

```lua
retry_after = window_size - elapsed
```

This provides predictable backoff behavior for clients.

---

## Advantages

* Smooths traffic spikes at window boundaries
* Memory efficient (only two counters)
* O(1) time complexity
* Very close to true sliding window accuracy
* Suitable for high-throughput systems

---

## Limitations

* Approximation assumes uniform distribution of requests
* Slight inaccuracies near bursty traffic patterns
* Less precise than Sliding Window Log
* Requires synchronized clocks in distributed systems

Despite these, real-world error rates are extremely low
(e.g., Cloudflare reports ~0.003% error at massive scale).

---

## When to Use Sliding Window Counter

Sliding Window Counter is ideal when:

* You need near-perfect rate accuracy
* Memory usage must be minimal
* Traffic is high-volume
* Boundary spikes must be smoothed
* Sliding Window Log is too expensive

Typical use cases include:

* Public APIs
* CDN edge throttling
* Distributed gateways
* User/IP-based quotas

---

## References

* [Rate Limiter – ByteByteGo](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)
* [Cloudflare Rate Limiting at Scale](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)


