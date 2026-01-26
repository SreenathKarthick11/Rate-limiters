# Rate-limiters

## Token Bucket Rate Limiter (v1)

Algorithm: Token Bucket  
Identifier: Client IP  

Parameters:
- Capacity: 5 tokens
- Refill rate: 0.5 tokens / second (5 per 10 seconds)

Redis key format:
rate:token_bucket:<client_ip>

Stored values:
- tokens
- last_refill_timestamp

