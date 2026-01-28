from fastapi import Request, HTTPException, status
from algorithms.token_bucket import token_bucket_limit

def rate_limit(capacity: int, refill_rate: float):
    async def dependency(request: Request):
        identifier = request.client.host

        result = token_bucket_limit(
            identifier=identifier,
            capacity=capacity,
            refill_rate=refill_rate,
        )

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(result.retry_after)},
            )

        return result

    return dependency
