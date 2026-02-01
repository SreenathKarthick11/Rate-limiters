# Fixed Window Counter Rate Limiter

## Overview

The **Fixed Window Counter** algorithm is one of the simplest and most widely used
rate limiting strategies.

It limits the number of requests allowed within a **fixed, discrete time window**
(e.g., per second, per minute).

Once the request count reaches a predefined threshold within the current window,
all subsequent requests are rejected **until the window resets**.

This approach is commonly used in:
- API gateways
- Authentication endpoints
- Basic traffic throttling systems

---

## Core Idea & Properties

- Time is divided into **fixed-size windows**
- Each window has a **counter**
- Every request increments the counter
- Requests are rejected once the limit is reached
- Counter resets at the start of the next window

| Property | Description |
|--------|------------|
| Window type | Fixed (non-overlapping) |
| Burst handling | Poor at window boundaries |
| Memory usage | Very low |
| State | Counter + window timestamp |
| Complexity | Very simple |

---

## Visual Model

Example: **3 requests per second**

```text
Time →
┌───────────┬───────────┬───────────┐
│  Window 1 │  Window 2 │  Window 3 │
│  (0–1s)   │  (1–2s)   │  (2–3s)   │
├───────────┼───────────┼───────────┤
│  Req ✓    │  Req ✓    │  Req ✓    │
│  Req ✓    │  Req ✓    │  Req ✓    │
│  Req ✓    │  Req ✓    │  Req ✓    │
│  Req ✗    │  Req ✗    │  Req ✗    │
└───────────┴───────────┴───────────┘
````

✔ First 3 requests per window are allowed
✗ Remaining requests are rejected until the next window

---

## Timeline Example

**Limit:** 3 requests / second

```text
Time (s):   0.0   0.3   0.6   0.9   1.1
Requests:   ✓     ✓     ✓     ✗     ✓
Window:    [ 0–1s ]    [ 1–2s ]
```

* First 3 requests in `0–1s` → allowed
* 4th request in same window → rejected
* Counter resets at `1.0s`

---

## Algorithm Steps

For each incoming request:

1. Compute the **current time window**
2. If the window has changed:

   * Reset the counter
   * Update window start time
3. Increment the counter
4. If counter ≤ limit:

   * Allow the request
5. Otherwise:

   * Reject the request

---

## Mathematical Model

Let:

* `W` = window size (seconds)
* `L` = request limit per window
* `t` = current timestamp

Window identifier:

```text
window_id = floor(t / W)
```

A request is allowed if:

```text
counter[window_id] < L
```

---

## Pseudocode

```lua
current_window = floor(now / window_size)

if current_window != stored_window then
    stored_window = current_window
    counter = 0
end

counter = counter + 1

if counter <= limit then
    allowed = true
else
    allowed = false
end

return allowed
```

This logic assumes **atomic counter updates** to prevent race conditions.

---

## Edge Case: Boundary Burst Problem

A major drawback of the fixed window algorithm is the **boundary spike problem**.

### Example: 5 requests per minute

```text
2:00:00 ─────────── 2:01:00 ─────────── 2:02:00
     ↑ ↑ ↑ ↑ ↑          ↑ ↑ ↑ ↑ ↑
     5 requests         5 requests
```

Although the limit is **5 requests per minute**,
between **2:00:30 and 2:01:30**, a total of **10 requests** are accepted.

This violates the intended rate limit.

---

## Advantages

* Very simple to implement
* Memory efficient
* Easy to reason about
* Works well for strict, human-aligned intervals
  (e.g., per minute, per hour)

---

## Limitations

* Allows bursts at window boundaries
* Not suitable for smooth rate enforcement
* Can violate true average rate limits
* Less fair under high concurrency

---

## When to Use Fixed Window

Fixed Window is suitable when:

* Simplicity is more important than precision
* Strict interval resets are acceptable
* Traffic patterns are predictable
* Slight bursts can be tolerated

Typical use cases include:

* Login attempts per minute
* Basic API quotas
* Admin or internal tools

---

## References

* [Rate Limiter – ByteByteGo](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)



---
