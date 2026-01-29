from fastapi import Request, HTTPException, status
from algorithms.token_bucket import token_bucket_limit
from algorithms.leaky_bucket import leaky_bucket_limit

def rate_limit(type: str, capacity: int, rate: float):
    async def dependency(request: Request):
        identifier = request.client.host

        if type == "token_bucket":
            allowed, info = token_bucket_limit(
                identifier=identifier,
                capacity=capacity,
                refill_rate=rate,
            )
        elif type == "leaky_bucket":
            allowed, info = leaky_bucket_limit(
                identifier=identifier,
                capacity=capacity,
                outflow_rate=rate,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid rate limiter type",
            )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(info.get("retry_after"))},
            )

        return info

    return dependency
